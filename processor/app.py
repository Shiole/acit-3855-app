import connexion
from connexion import NoContent
from datetime import datetime
import requests
import yaml
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
import json
import os
from flask_cors import CORS, cross_origin

with open("log_conf.yaml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("basicLogger")

with open("app_conf.yaml", "r") as f:
    app_config = yaml.safe_load(f.read())
    data_file = app_config["datastore"]["filename"]
    ENDPOINT = app_config["eventstore"]["url"]


def get_stats():
    logger.info("Starting stats retrieval...")

    if os.path.isfile(data_file):
        with open(data_file, "r") as f:
            data = json.load(f)

        data.pop("last_updated")

        logger.debug(f"Current recorded stats: {data}")
        logger.info("Stats retrieval complete")

        return data, 200
    else:
        logger.error("Error: Stats file does not exist")
        return "Statistics do not exist", 404


def populate_stats():
    """ Periodically update stats """
    logger.info("Start Periodic Processing...")

    if os.path.isfile(data_file):
        with open(data_file, "r") as f:
            stats = json.load(f)
    else:
        stats = {
            "num_orders": 0,
            "max_order_quantity": 0,
            "max_order_total": 0,
            "num_deliveries": 0,
            "max_delivery_distance": 0,
            "last_updated": "2023-10-12 09:30:05.309015"
        }

    last_updated = stats["last_updated"]
    cur_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    # Get Order logs
    orders_response = requests.get(
        f"{ENDPOINT}/getorders?timestamp={last_updated}")
    orders_results = orders_response.json()

    # Process logs
    if orders_response.status_code == 200:
        logger.info(
            f"Received {len(orders_results)} Order events at {cur_datetime}")

        stats["num_orders"] += len(orders_results)

        if len(orders_results):
            stats["max_order_quantity"] = max(
                map(lambda o: o["order_quantity"], orders_results))
            stats["max_order_total"] = max(
                map(lambda o: o["order_total"], orders_results))
    else:
        logger.error(
            f"Getting Orders returned status code {orders_response.status_code}")
        return

    # Get Delivery logs
    deliveries_response = requests.get(
        f"{ENDPOINT}/getdeliveries?timestamp={last_updated}")
    deliveries_results = deliveries_response.json()

    # Process logs
    if deliveries_response.status_code == 200:
        logger.info(
            f"Received {len(orders_results)} Delivery events at {cur_datetime}")

        stats["num_deliveries"] += len(deliveries_results)

        if len(deliveries_results):
            stats["max_delivery_distance"] = max(
                map(lambda d: d["delivery_distance"], deliveries_results))

    else:
        logger.error(
            f"Getting Deliveries returned status code {deliveries_response.status_code}")
        return

    stats["last_updated"] = cur_datetime

    with open(data_file, "w") as f:
        json.dump(stats, f)

    logger.debug(f"Updated processed data: {stats}")
    logger.info("Periodic processing complete")


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  "interval",
                  seconds=app_config["scheduler"]["period_sec"]
                  )
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, debug=True)
