import json
import logging
import logging.config
import os.path
import connexion
import yaml
from connexion import NoContent
import datetime
from pykafka import KafkaClient

import requests

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def report_calorie_intake(body):

    logger.debug(("DEBUG: " + str(body)))
    logger.info("INFO: Received event Calorie Intake request with a unique id of " + str(body['client_id']))

    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic_name = app_config["events"]["topic"]
    topic = client.topics[str.encode(topic_name)]

    producer = topic.get_sync_producer()
    logger.info("this inst working")
    msg = {"type": "ci",
           "datetime":
                datetime.datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))


    logger.info("INFO: Returned event Calorie Intake response " + str(body['client_id']) + " with status 201")

    return NoContent, 201


def report_weight(body):

    logger.debug(("DEGBUG: " + str(body)))
    logger.info("INFO: Received event Weight request with a unique id of " + str(body['client_id']))

    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic_name = app_config["events"]["topic"]
    topic = client.topics[str.encode(topic_name)]
    producer = topic.get_sync_producer()

    msg = {"type": "w",
           "datetime":
               datetime.datetime.now().strftime(
                   "%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))


    logger.info("INFO: Returned event Weight response " + str(body['client_id']) + " with status 201")

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')

app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)

