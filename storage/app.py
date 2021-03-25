import json
import os.path
import connexion
from connexion import NoContent
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base

from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread

from calorie_intake import CalorieIntake
from weight import Weight

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

DB_ENGINE = create_engine("mysql+pymysql://" + app_config["datastore"]["user"] + ":" + app_config["datastore"]["password"] + "@" + app_config["datastore"]["hostname"] + ":" + str(app_config["datastore"]["port"]) + "/" + app_config["datastore"]["db"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger.info("Connecting to DB. Hostname: %s, Port: %d" % (app_config["datastore"]["hostname"], app_config["datastore"]["port"]))

def report_calorie_intake(body):

    session = DB_SESSION()

    ci = CalorieIntake(body['client_id'],
                   body['device_id'],
                   body['calorie_intake'],
                   body['timestamp'])

    session.add(ci)

    session.commit()
    session.close()

    logger.debug(("DEBUG: Stored event Calorie Intake request with a unique id of " + str(body['client_id'])))

    return NoContent, 201
#
#
def report_weight(body):

    session = DB_SESSION()

    wt = Weight(body['client_id'],
                   body['device_id'],
                   body['weight'],
                   body['timestamp'])

    session.add(wt)

    session.commit()
    session.close()

    logger.debug(("DEBUG: Stored event Weight request with a unique id of " + str(body['client_id'])))

    return NoContent, 201


def get_calorie_intake_reports(timestamp):

    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

    reports = session.query(CalorieIntake).filter(CalorieIntake.date_created >= timestamp_datetime)

    results_list = []

    for report in reports:
        results_list.append(report.to_dict())

    session.close()

    logger.info("Query for Calorie Intake reports after %s returns %d results" % (timestamp, len(results_list)))

    return results_list, 200


def get_weight_reports(timestamp):

    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

    reports = session.query(Weight).filter(Weight.date_created >= timestamp_datetime)

    results_list = []

    for report in reports:
        results_list.append(report.to_dict())

    session.close()

    logger.info("Query for Weight reports after %s returns %d results" % (timestamp, len(results_list)))

    return results_list, 200


def process_messages():

    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg["payload"]

        if msg["type"] == "ci":
            report_calorie_intake(payload)
        elif msg["type"] == "w":
            report_weight(payload)

        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')

app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":

    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()

    app.run(port=8090)

