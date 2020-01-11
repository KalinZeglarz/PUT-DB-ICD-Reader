"""Contains main block"""
import json
import logging
import sys
from datetime import datetime

from icd_reader import logger
from icd_reader.classes.DbController import DbController
from icd_reader.classes.IcdMapper import IcdMapper
from icd_reader.classes.IcdWikipediaMapper import IcdWikipediaMapper
from icd_reader.classes.MySqlController import MySqlController

configuration: dict

logger.initialize()


def _load_configuration():
    global configuration

    with open('resources/configuration.json', 'r') as f:
        configuration = json.load(f)
        logging.info("Loaded configuration from path 'resources/configuration.json'")


def _input_argument() -> list:
    input_data: list = []
    if sys.argv.count('--input') > 0:
        arg_index: int = sys.argv.index('--input')
        if sys.argv[arg_index + 1].lower() == "json":
            file = open(sys.argv[arg_index + 2], 'r')
            input_json: dict = json.load(file.read())
            file.close()
            for code in input_json['codes']:
                input_data.append(code)
        elif sys.argv[arg_index + 1].lower() == "argument":
            for code in sys.argv[arg_index + 2].split(','):
                input_data.append(code)
    else:
        print("ERROR: missing '--input' argument", file=sys.stderr)
        sys.exit(1)
    return input_data


def _mode_argument() -> str:
    if sys.argv.count('--mode') > 0:
        arg_index: int = sys.argv.index('--mode')
        if sys.argv[arg_index + 1].lower() == "icd10-icd11":
            return 'icd10-icd11'
        elif sys.argv[arg_index + 1].lower() == "icd11-icd10":
            return 'icd11-icd10'
        elif sys.argv[arg_index + 1].lower() == "save-to-db":
            return 'save-to-db'
        elif sys.argv[arg_index + 1].lower() == "prolog":
            return 'prolog'
        else:
            print("ERROR: unrecognized '--mode' value", file=sys.stderr)
            sys.exit(1)
    else:
        print("ERROR: missing '--mode' argument", file=sys.stderr)
        sys.exit(1)


def _main():
    _load_configuration()
    icd_mapper: IcdMapper = IcdMapper(
        client_id=configuration['icd-api-credentials']['client-id'],
        client_secret=configuration['icd-api-credentials']['client-secret']
    )
    db_controller: DbController = MySqlController(
        host=configuration['db-parameters']['host'],
        user=configuration['db-parameters']['user'],
        password=configuration['db-parameters']['password']
    )
    wikipedia_mapper: IcdWikipediaMapper = IcdWikipediaMapper("resources/codeSpaces.json")

    input_data: list = []
    mode: str

    # mode argument (required)
    mode = _mode_argument()

    # input data argument
    if mode != 'prolog':
        input_data = _input_argument()

    if mode == 'icd10-icd11':
        for icd10_code in input_data:
            print(icd_mapper.icd_10_to_icd_11(icd10_code))

    elif mode == 'save-to-db':
        for icd10_code in input_data:
            icd11_code: str = icd_mapper.icd_10_to_icd_11(icd10_code)
            if icd11_code == "":
                continue
            disease_name: str = icd_mapper.get_icd_10_name(icd10_code)
            eng_title, eng_url, pol_url = wikipedia_mapper.get_disease_wikipedia_data(icd10_code)
            db_controller.add_disease_entry(disease_name)
            id_disease: int = db_controller.get_disease_id_by_name(disease_name)
            db_controller.add_icd_codes(id_disease, icd_mapper.split_icd_10_code(icd10_code), icd11_code)
            db_controller.add_wiki_info(id_disease, 'eng', eng_title, eng_url)
            db_controller.add_wiki_info(id_disease, 'pol', '', pol_url)

    elif mode == 'prolog':
        date_time_obj = datetime.now()
        timestamp_str: str = date_time_obj.strftime("%d-%b-%Y_%H-%M-%S")

        file = open('prolog_{0}.pl'.format(timestamp_str), 'w+')
        file.write(db_controller.export_to_prolog())
        file.close()


if __name__ == "__main__":
    _main()
