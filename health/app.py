from connexion import FlaskApp, NoContent
from datetime import datetime
import requests
import yaml
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
import json
import os
from flask_cors import CORS
import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yaml"
    log_conf_file = "/config/log_conf.yaml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yaml"
    log_conf_file = "log_conf.yaml"


with open(app_conf_file, "r") as f:
    app_config = yaml.safe_load(f.read())
    data_file = app_config["datastore"]["filename"]
    receiver_endpoint = app_config["eventstore"]["receiver_url"]
    storage_endpoint = app_config["eventstore"]["storage_url"]
    processing_endpoint = app_config["eventstore"]["processing_url"]
    audit_endpoint = app_config["eventstore"]["audit_url"]

with open(log_conf_file, "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger("basicLogger")

logger.info(f"App Conf File: {app_conf_file}")
logger.info(f"Log Conf File: {log_conf_file}")


def get_health():
    logger.info("Starting stats retrieval...")

    if os.path.isfile(data_file):
        with open(data_file, "r") as f:
            data = json.load(f)

        logger.debug(f"Current recorded stats: {data}")
        logger.info("Stats retrieval complete")

        return data, 200
    else:
        logger.error("Error: Stats file does not exist")
        return "Statistics do not exist", 404


def populate_health():
    """ Periodically update stats """
    logger.info("Start Periodic Processing...")

    if os.path.isfile(data_file):
        with open(data_file, "r") as f:
            stats = json.load(f)
    else:
        stats = {
            "Receiver": "Down",
            "Storage": "Down",
            "Processing": "Down",
            "Audit": "Down",
            "last_updated": "2023-11-16 10:53:05.309015"
        }

    last_updated = stats["last_updated"]
    cur_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    # Get service health
    receiver_health = requests.get(f"{receiver_endpoint}/health")
    storage_health = requests.get(f"{storage_endpoint}/health")
    processing_health = requests.get(f"{processing_endpoint}/health")
    audit_health = requests.get(f"{audit_endpoint}/health")

    stats["last_updated"] = cur_datetime

    with open(data_file, "w") as f:
        json.dump(stats, f)

    logger.debug(f"Updated processed data: {stats}")
    logger.info("Periodic processing complete")


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_health,
                  "interval",
                  seconds=app_config["scheduler"]["period_sec"]
                  )
    sched.start()


app = FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8120, use_reloader=False)
