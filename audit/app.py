from connexion import FlaskApp
import swagger_ui_bundle
from pykafka import KafkaClient
import logging
import logging.config
import yaml
import json

with open("log_conf.yaml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("basicLogger")

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    kafka_server = app_config["events"]["hostname"]
    kafka_port = app_config["events"]["port"]
    kafka_topic = app_config["events"]["topic"]


def get_order_event(index):
    """ Get Order event in History """
    hostname = f'{kafka_server}:{kafka_port}'
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(kafka_topic)]

    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)

    logger.info(f"Retrieving Order at index {index}")

    try:
        messages = []
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg["type"] == "order":
                messages.append(msg["payload"])

        return messages[index], 200
    except:
        logger.error("No more messages found")
        logger.error(f"Could not find Order at index {index}")
    return {"message": "Not Found"}, 404


def get_delivery_event(index):
    """ Get Delivery event in History """
    hostname = f'{kafka_server}:{kafka_port}'
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(kafka_topic)]

    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)

    logger.info(f"Retrieving Delivery at index {index}")

    try:
        messages = []
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg["type"] == "delivery":
                messages.append(msg)

        return messages[index], 200
    except:
        logger.error("No more messages found")
        logger.error(f"Could not find Delivery at index {index}")
    return {"message": "Not Found"}, 404


app = FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110)
