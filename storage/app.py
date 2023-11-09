from connexion import FlaskApp
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from base import Base
from orders import Orders
from deliveries import Deliveries
import yaml
import logging
import logging.config
import datetime
import json
import time
from pykafka import KafkaClient
from pykafka.common import OffsetType
from pykafka.exceptions import SocketDisconnectedError, LeaderNotAvailable
from threading import Thread

with open('./app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    kafka_server = app_config["events"]["hostname"]
    kafka_port = app_config["events"]["port"]
    kafka_topic = app_config["events"]["topic"]
    max_retry = app_config["max_retry"]
    sleep = app_config["sleep"]

DB_ENGINE = create_engine(
    f"mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

with open('./log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')


def get_orders(start_timestamp, end_timestamp):
    """ Gets new orders after the timestamp"""
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(
        start_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    end_timestamp_datetime = datetime.datetime.strptime(
        end_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    orders = session.query(Orders).filter(
        and_(Orders.date_created >= start_timestamp_datetime,
             Orders.date_created < end_timestamp_datetime))

    results_list = []

    for o in orders:
        results_list.append(o.to_dict())

    session.close()

    logger.info(
        f"Query for Orders after {start_timestamp} returns {len(results_list)} results")

    return results_list, 200


def get_deliveries(start_timestamp, end_timestamp):
    """ Gets new deliveries after the timestamp"""
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(
        start_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    end_timestamp_datetime = datetime.datetime.strptime(
        end_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    deliveries = session.query(Deliveries).filter(
        and_(Deliveries.date_created >= start_timestamp_datetime,
             Deliveries.date_created < end_timestamp_datetime))

    results_list = []

    for d in deliveries:
        results_list.append(d.to_dict())

    session.close()

    logger.info(
        f"Query for Deliveries after {start_timestamp} returns {len(results_list)} results")

    return results_list, 200


def process_messages():
    """ Process event messages """
    hostname = f"{kafka_server}:{kafka_port}"
    cur_retry = 0

    while cur_retry < max_retry:
        logger.info(f"Trying to connect to Kafka. Current retry: {cur_retry}")
        cur_retry += 1

        try:
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(kafka_topic)]
            break
        except Exception as e:
            logger.error(f"Connection failed")
            time.sleep(sleep)

    # Create a consumer on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info(f"Message: {msg}")

        payload = msg["payload"]

        if msg["type"] == "order":
            # Store order payload to the DB
            logger.info(
                f"Received event Order request with a trace id of {payload['trace_id']}")
            session = DB_SESSION()

            oe = Orders(payload['customer_name'],
                        payload['customer_phone'],
                        payload['is_delivery'],
                        payload['order_address'],
                        payload['burger_name'],
                        payload['order_quantity'],
                        payload['order_total'],
                        payload['order_tip'],
                        payload['order_timestamp'],
                        payload['trace_id'])

            session.add(oe)
            session.commit()
            session.close()

            logger.debug(
                f"Stored order event with trace id {payload['trace_id']}")
        elif msg["type"] == "delivery":
            # Store delivery payload to the DB
            logger.info(
                f"Received event Delivery request with a trace id of {payload['trace_id']}")

            session = DB_SESSION()

            de = Deliveries(payload['order_id'],
                            payload['driver_id'],
                            payload['assignment_timestamp'],
                            payload['fulfilment_timestamp'],
                            payload['delivery_distance'],
                            payload['delivery_tip'],
                            payload['trace_id'])

            session.add(de)
            session.commit()
            session.close()

            logger.info(
                f"Delivery with trace id {payload['trace_id']} added to database")

        # Commit the new message as being read
        consumer.commit_offsets()


app = FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)
logger.info(
    f"Connecting to DB. Hostname: {app_config['datastore']['hostname']}, Port: {app_config['datastore']['port']}")

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon = True
    t1.start()
    app.run(port=8090)
