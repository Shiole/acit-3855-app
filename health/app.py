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
    receiver = app_config["eventstore"]["receiver"]
    storage = app_config["eventstore"]["storage"]
    processing = app_config["eventstore"]["processing"]
    audit = app_config["eventstore"]["audit"]

with open(log_conf_file, "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger("basicLogger")

logger.info(f"App Conf File: {app_conf_file}")
logger.info(f"Log Conf File: {log_conf_file}")


def get_health():
    logger.info("Retreiving health stats...")

    if os.path.isfile(data_file):
        with open(data_file, "r") as f:
            data = json.load(f)

        logger.debug(f"Current recorded health: {data}")
        logger.info("Health retrieval complete")

        return data, 200
    else:
        logger.error("Error: Health file does not exist")
        return "Health stats do not exist", 404


def get_service_health(service):
    logger.info(f"Checking {service} health...")
    status = "Down"
    try:
        res = requests.get(f"{app_config['eventstore'][service]}", timeout=int(
            app_config["timeout"]["timeout_sec"]))
        if res.status_code == 200:
            status = "Running"
            logger.info(f"{service} service is RUNNING")
    except:
        logger.error(f"{service} service is DOWN")
        pass

    return status


def populate_health():
    """ Periodically update health """
    logger.info("Start Periodic Health Check...")

    if os.path.isfile(data_file):
        with open(data_file, "r") as f:
            health = json.load(f)
    else:
        health = {
            "receiver": "Down",
            "storage": "Down",
            "processing": "Down",
            "audit": "Down",
            "last_updated": "2023-11-21T10:53:05Z"
        }

    # Get service health
    services = ["receiver", "storage", "processing", "audit"]
    health = {}

    for s in services:
        health[s] = get_service_health(s)

    health["last_updated"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(data_file, "w") as f:
        json.dump(health, f)

    logger.debug(f"Updated health data: {health}")
    logger.info("Health status check complete")


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
