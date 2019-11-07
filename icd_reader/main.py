"""Contains main block"""
import json
import logging

from icd_reader import logger

configuration: dict

logger.initialize()


def _load_configuration():
    global configuration

    # Read JSON data into the datastore variable
    with open('resources/configuration.json', 'r') as f:
        configuration = json.load(f)
        logging.info("Loaded configuration from path 'resources/configuration.json'")


if __name__ == "__main__":
    _load_configuration()
