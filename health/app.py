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
    receiver = app_config["eventstore"]["receiver_url"]
    storage = app_config["eventstore"]["storage_url"]
    processing = app_config["eventstore"]["processing_url"]
    audit = app_config["eventstore"]["audit_url"]

with open(log_conf_file, "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger("basicLogger")

logger.info(f"App Conf File: {app_conf_file}")
logger.info(f"Log Conf File: {log_conf_file}")


def get_health(service):
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
    """ Periodically update stats """
    logger.info("Start Periodic Processing...")

    # Get service health
    services = ["receiver", "storage", "processing", "audit"]
    health = {}

    for s in services:
        health[s] = get_health(s)

    health["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    with open(data_file, "w") as f:
        json.dump(health, f)


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
