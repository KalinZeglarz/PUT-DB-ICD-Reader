"""Contains main block"""
import json
import logging
import sys

from icd_reader import logger
from icd_reader.classes.IcdMapper import IcdMapper

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
    else:
        print("ERROR: missing '--mode' argument", file=sys.stderr)
        sys.exit(1)


def _main():
    _load_configuration()
    icd_mapper: IcdMapper = IcdMapper(
        configuration['icd-api-credentials']['client-id'],
        configuration['icd-api-credentials']['client-secret']
    )
    input_data: list = []
    mode: str

    # input data argument (required)
    input_data = _input_argument()

    # mode argument (required)
    mode = _mode_argument()

    if mode == 'icd10-icd11':
        for code in input_data:
            print(icd_mapper.icd_10_to_icd_11(code))


if __name__ == "__main__":
    _main()
