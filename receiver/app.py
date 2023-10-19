from connexion import FlaskApp, NoContent
import yaml
import logging
import logging.config
import uuid
import datetime
import json
from pykafka import KafkaClient

with open('./app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    kafka_server = app_config["events"]["hostname"]
    kafka_port = app_config["events"]["port"]
    kafka_topic = app_config["events"]["topic"]

with open('./log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')


def create_order(body):
    trace_id = str(uuid.uuid4())
    body["trace_id"] = trace_id
    logger.info(
        f"Received event Order request with a trace id of {trace_id}")

    client = KafkaClient(hosts=f'{kafka_server}:{kafka_port}')
    topic = client.topics[str.encode(kafka_topic)]
    producer = topic.get_sync_producer()
    msg = {"type": "order",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": body
           }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(
        f"Received event Order response (Id: {trace_id}) with status {201}")

    return NoContent, 201


def schedule_delivery(body):
    trace_id = str(uuid.uuid4())
    body["trace_id"] = trace_id
    logger.info(
        f"Received event Delivery request with a trace id of {trace_id}")

    client = KafkaClient(hosts=f'{kafka_server}:{kafka_port}')
    topic = client.topics[str.encode(kafka_topic)]
    producer = topic.get_sync_producer()
    msg = {"type": "delivery",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": body
           }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(
        f"Received event Delivery response (Id: {trace_id}) with status {201}")

    return NoContent, 201


app = FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
