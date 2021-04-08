import json
import os.path
import connexion
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from connexion import NoContent
import datetime
from flask_cors import CORS, cross_origin


import yaml
import logging.config


#with open('app_conf.yaml', 'r') as f:
#    app_config = yaml.safe_load(f.read())

#with open('log_conf.yaml', 'r') as f:
#    log_config = yaml.safe_load(f.read())
#    logging.config.dictConfig(log_config)

#logger = logging.getLogger('basicLogger')

import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yaml"
    log_conf_file = "/config/log_conf.yaml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yaml"
    log_conf_file = "log_conf.yaml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
    
# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    
logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

def populate_stats():

    logger.info("Start Processing")
    stats = {}

    timestamp = '2021-01-14T10:32:48Z'

    if os.path.isfile(app_config["datastore"]["filename"]):

        stats_json = open(app_config["datastore"]["filename"])

        data = stats_json.read()
        stats = json.loads(data)

        stats_json.close()
        timestamp = stats["last_updated"]
        current_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    response = requests.get(app_config["eventstore"]["url"] + "/calorie-intake?start_timestamp=" + timestamp + "&end_timestamp=" + current_timestamp)

    if response.status_code == 200:
        if "num_ci_reports" in stats.keys():
            stats["num_ci_reports"] = stats["num_ci_reports"] + len(response.json())
        else:
            stats["num_ci_reports"] = len(response.json())

        for event in response.json():
            if "max_ci_report" in stats.keys() and event["calorie_intake"] > stats["max_ci_report"]:
                stats["max_ci_report"] = event["calorie_intake"]
            elif "max_ci_report" not in stats.keys():
                stats["max_ci_report"] = event["calorie_intake"]

            if "min_ci_report" in stats.keys() and event["calorie_intake"] < stats["min_ci_report"]:
                stats["min_ci_report"] = event["calorie_intake"]
            elif "min_ci_report" not in stats.keys():
                stats["min_ci_report"] = event["calorie_intake"]

        logger.info("Processed " + str(len(response.json())) + " CI reports")

    else:
        logger.error("No reports processed due to error: " + str(response.status_code))

    response = requests.get(app_config["eventstore"]["url"] + "/weight?start_timestamp=" + timestamp + "&end_timestamp=" + current_timestamp)

    if response.status_code == 200:
        if "num_w_reports" in stats.keys():
            stats["num_w_reports"] = stats["num_w_reports"] + len(response.json())
        else:
            stats["num_w_reports"] = len(response.json())

        for event in response.json():
            if "max_w_report" in stats.keys() and event["weight"] > stats["max_w_report"]:
                stats["max_w_report"] = event["weight"]
            elif "max_w_report" not in stats.keys():
                stats["max_w_report"] = event["weight"]

            if "min_w_report" in stats.keys() and event["weight"] < stats["min_w_report"]:
                stats["min_w_report"] = event["weight"]
            elif "min_w_report" not in stats.keys():
                stats["min_w_report"] = event["weight"]

        logger.info("Processed " + str(len(response.json())) + " Weight reports")

    else:
        logger.error("No reports processed due to error: " + str(response.status_code))

    #stats["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    stats["last_updated"] = current_timestamp

    stats_json = open(app_config["datastore"]["filename"], "w")

    stats_json.write(json.dumps(stats))

    stats_json.close()

    logger.debug(str(stats))
    logger.info("Processing Complete")


def get_stats():
    logger.info("Start Get Stats Request")

    stats = {}

    if os.path.isfile(app_config["datastore"]["filename"]):

        stats_json = open(app_config["datastore"]["filename"])

        data = stats_json.read()
        stats = json.loads(data)

        stats_json.close()

        return stats, 200

    else:
        logger.error("Statistics do not exist")

        return "Statistics do not exist", 404


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
      CORS(app.app)
      app.app.config['CORS_HEADERS'] = 'Content-Type'

#app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)
app.add_api("openapi.yaml", base_path="/processing", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)

