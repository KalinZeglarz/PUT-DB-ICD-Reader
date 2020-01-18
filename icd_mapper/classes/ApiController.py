import json
import logging
import os

from flask import Response

from icd_mapper import logger
from icd_mapper.classes.IcdMapper import IcdMapper
from icd_mapper.classes.IcdWikipediaMapper import IcdWikipediaMapper
from icd_mapper.classes.db.DbController import DbController
from icd_mapper.classes.db.SqlController import MySqlController

logger.initialize()

icd_mapper: IcdMapper
db_controller: DbController
wikipedia_mapper: IcdWikipediaMapper


def _check_env_variables(base_key: str, configuration: dict) -> dict:
    for key in configuration:
        key_env: str = key.replace('-', '_')
        if type(configuration[key]) == dict:
            configuration[key] = _check_env_variables(base_key + key_env + '_', configuration[key])
        elif os.getenv(base_key + key_env) is not None:
            configuration[key] = os.environ[base_key + key_env]
    return configuration


def load_configuration():
    global icd_mapper
    global db_controller
    global wikipedia_mapper

    with open('./resources/configuration.json', 'r') as f:
        configuration = json.load(f)
        logging.info("Loaded configuration from path 'resources/configuration.json'")
    configuration = _check_env_variables('', configuration)
    db_controller = MySqlController(
        database=configuration['db-parameters']['database'],
        host=configuration['db-parameters']['host'],
        user=configuration['db-parameters']['user'],
        password=configuration['db-parameters']['password']
    )
    icd_mapper = IcdMapper(
        client_id=configuration['icd-api-credentials']['client-id'],
        client_secret=configuration['icd-api-credentials']['client-secret']
    )
    wikipedia_mapper = IcdWikipediaMapper("./resources/codeSpaces.json")


def add_or_update_icd10(request) -> Response:
    global icd_mapper
    global db_controller
    global wikipedia_mapper

    if 'data' not in request.get_json():
        return Response(status=400)

    input_data: list = request.get_json()['data']
    additional_languages: list = request.get_json()['additionalLanguages']
    result: dict = {'notFound': []}
    for icd10_code in input_data:
        not_found_languages: list = _process_icd10_code(icd10_code, additional_languages)
        if not not_found_languages:
            continue
        if not_found_languages[0] is None:
            result['notFound'].append({'icd10': icd10_code})
        elif len(not_found_languages) > 0:
            result['notFound'].append({'icd10': icd10_code, "languages": not_found_languages})
    return Response(response=json.dumps(result), status=201, mimetype='application/json')


def _process_icd10_code(icd10_code: str, additional_languages: list) -> list:
    icd11_code: str = icd_mapper.icd_10_to_icd_11(icd10_code)
    if icd11_code == "":
        return [None]

    disease_name: str = icd_mapper.get_icd_10_name(icd10_code)
    wiki_infos: list = wikipedia_mapper.get_disease_wikipedia_data(icd10_code, additional_languages)
    db_controller.add_disease_entry(disease_name)
    id_disease: int = db_controller.get_disease_id_by_name(disease_name)
    db_controller.add_icd_codes(id_disease, icd_mapper.split_icd_10_code(icd10_code), icd11_code)

    found_languages: list = []
    for wiki_info in wiki_infos:
        found_languages.append(wiki_info[0])
        db_controller.add_wiki_info(id_disease, wiki_info[0], wiki_info[1], wiki_info[2])

    result: list = []
    for additional_language in additional_languages:
        if additional_language not in found_languages:
            result.append(additional_language)
    return result


def get_icd10(request, code: str):
    response_format: str = request.args.get('format')
    result: list = db_controller.get_icd10_info(code)

    if not result:
        return Response(status=404)

    if response_format == "json-pretty":
        return Response(response=json.dumps(result, indent=3), status=200, mimetype='application/json')
    else:
        return Response(response=json.dumps(result), status=200, mimetype='application/json')


def get_icd11(request, code: str):
    response_format: str = request.args.get('format')
    result: list = db_controller.get_icd11_info(code)
    if not result:
        return Response(status=404)

    if response_format == "json-pretty":
        return Response(response=json.dumps(result, indent=3), status=200, mimetype='application/json')
    else:
        return Response(response=json.dumps(result), status=200, mimetype='application/json')


def get_disease(request, id_disease: int):
    response_format: str = request.args.get('format')
    result: list = db_controller.get_disease_info([id_disease])
    if not result:
        return Response(status=404)

    if response_format == "json-pretty":
        return Response(response=json.dumps(result, indent=3), status=200, mimetype='application/json')
    else:
        return Response(response=json.dumps(result), status=200, mimetype='application/json')


def add_additional_info(request) -> Response:
    data: dict = request.get_json()

    if not {'diseaseId', 'type', 'author', 'info'} <= request.get_json().keys():
        return Response(status=400)

    db_controller.add_additional_info(data['diseaseId'], data['type'], data['author'], data['info'])
    return Response(status=201)


def modify_additional_info(request) -> Response:
    data: dict = request.get_json()

    if not {'infoId', 'type', 'author', 'info'} <= request.get_json().keys():
        return Response(status=400)

    db_controller.modify_additional_info(data['infoId'], data['type'], data['author'], data['info'])
    return Response(status=201)


def delete_additional_info(id_disease: int) -> Response:
    db_controller.delete_additional_info(id_disease)
    return Response(status=200)
