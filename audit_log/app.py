import json
#import os.path
import connexion
#import requests
#from apscheduler.schedulers.background import BackgroundScheduler
#from connexion import NoContent
#import datetime
from flask_cors import CORS, cross_origin
import yaml
import logging.config
from pykafka import KafkaClient
#from pykafka.common import OffsetType
#from threading import Thread

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
    
def get_calorie_intake_report(index):

    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)

    logger.info("Retrieving CI at index %d" % index)

    count = 0
    reading = None

    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg["type"] == "ci":
                logger.info("Count %d" % count)

                if count == index:
                    reading = msg["payload"]
                    return reading, 200

                count += 1
    except:

        logger.error("No more messages found")

    logger.error("Could not find BP at index %d" % index)
    return {"message": "Not Found"}, 404


def get_weight_report(index):

    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)

    logger.info("Retrieving W at index %d" % index)

    count = 0
    reading = None

    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg["type"] == "w":
                logger.info("Count %d" % count)

                if count == index:
                    reading = msg["payload"]
                    return reading, 200

                count += 1
    except:

        logger.error("No more messages found")

    logger.error("Could not find BP at index %d" % index)
    return {"message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110)
