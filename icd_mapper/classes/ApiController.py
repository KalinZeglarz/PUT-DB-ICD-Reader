import json
import logging
import os
from multiprocessing import Pool

from flask import Response

from icd_mapper import logger
from icd_mapper.classes.IcdMapper import IcdMapper
from icd_mapper.classes.IcdWikipediaMapper import IcdWikipediaMapper
from icd_mapper.classes.db.DbController import DbController
from icd_mapper.classes.db.SqlController import SqlController

logger.initialize()

icd_mapper: IcdMapper
db_controller: DbController
wikipedia_mapper: IcdWikipediaMapper
proc_pool: Pool = None
configuration: dict = {}


def _check_env_variables(base_key: str, configuration: dict) -> dict:
    for key in configuration:
        key_env: str = key.replace('-', '_')
        if type(configuration[key]) == dict:
            configuration[key] = _check_env_variables(base_key + key_env + '_', configuration[key])
        elif os.getenv(base_key + key_env) is not None:
            configuration[key] = os.environ[base_key + key_env]
    return configuration


def load_configuration():
    global icd_mapper, db_controller, wikipedia_mapper, configuration

    with open('./resources/configuration.json', 'r') as f:
        configuration = json.load(f)
        logging.info("Loaded configuration from path 'resources/configuration.json'")
    configuration = _check_env_variables('', configuration)
    db_controller = SqlController(
        database=configuration['db']['database'],
        host=configuration['db']['host'],
        user=configuration['db']['user'],
        password=configuration['db']['password']
    )
    icd_mapper = IcdMapper(
        client_id=configuration['icd-api-credentials']['client-id'],
        client_secret=configuration['icd-api-credentials']['client-secret']
    )
    wikipedia_mapper = IcdWikipediaMapper("./resources/codeSpaces.json")


def start_process_pool():
    global proc_pool, configuration

    pool_size = int(configuration["server"]["pool-size"])
    if pool_size > 0:
        proc_pool = Pool(pool_size)
        logging.info("Started process pool with {} processes".format(pool_size))
    else:
        logging.info("Not using process pool")


def _check_database_connection() -> Response:
    if not db_controller.check_connection():
        return Response(response="No database connection", status=503)
    return Response(status=0)


def add_or_update_icd10(request) -> Response:
    global icd_mapper, db_controller, wikipedia_mapper, proc_pool

    db_connection = _check_database_connection()
    if db_connection.status_code != 0:
        return db_connection

    icd10_codes: list = request.get_json()['data']
    additional_languages: list = request.get_json()['additionalLanguages']
    result: dict
    if proc_pool:
        result = _async_add_or_update_icd10(icd10_codes, additional_languages)
    else:
        result = _sync_add_or_update_icd10(icd10_codes, additional_languages)

    return Response(response=json.dumps(result), status=201, mimetype='application/json')


def _async_add_or_update_icd10(icd10_codes: list, additional_languages: list) -> dict:
    pool_results: dict = {}
    for icd10_code in icd10_codes:
        args: tuple = (
            icd10_code,
            additional_languages,
            icd_mapper,
            wikipedia_mapper,
        )
        pool_results[icd10_code] = proc_pool.apply_async(func=_process_icd10_code, args=args)

    return _process_pool_results(pool_results, icd10_codes)


def _sync_add_or_update_icd10(icd10_codes: list, additional_languages: list) -> dict:
    result: dict = {'notFound': []}
    for icd10_code in icd10_codes:
        processing_result: dict = _process_icd10_code(icd10_code, additional_languages, icd_mapper, wikipedia_mapper)
        result.update(_process_result(processing_result, icd10_code))
    return result


def _process_pool_results(pool_results: dict, icd10_codes) -> dict:
    result: dict = {'notFound': []}
    for icd10_code in icd10_codes:
        pool_result: dict = pool_results[icd10_code].get()
        result.update(_process_result(pool_result, icd10_code))
    return result


def _process_result(processing_result: dict, icd10_code: str) -> dict:
    result: dict = {'notFound': []}

    if processing_result == {}:
        result['notFound'].append({'icd10_code': icd10_code})
        return result
    if len(processing_result['not_found_languages']) > 0:
        result['notFound'].append({'icd10_code': icd10_code, "languages": processing_result['not_found_languages']})

    _add_disease_and_codes(processing_result['disease_name'], icd10_code, processing_result['icd11_code'])

    id_disease: int = db_controller.get_disease_id_by_name(processing_result['disease_name'])
    for parent in processing_result['relations']['parent']:
        _add_disease_and_codes(parent['disease_name'], parent['icd10_code'], parent['icd11_code'])
        id_disease_rel: int = db_controller.get_disease_id_by_icd10(parent['icd10_code'])[0]
        db_controller.add_disease_relation(id_disease, id_disease_rel, "child")
        db_controller.add_disease_relation(id_disease_rel, id_disease, "parent")

    for child in processing_result['relations']['children']:
        _add_disease_and_codes(child['disease_name'], child['icd10_code'], child['icd11_code'])
        id_disease_rel: int = db_controller.get_disease_id_by_icd10(child['icd10_code'])[0]
        db_controller.add_disease_relation(id_disease, id_disease_rel, "parent")
        db_controller.add_disease_relation(id_disease_rel, id_disease, "child")

    for wiki_info in processing_result['wiki_infos']:
        processing_result['found_languages'].append(wiki_info[0])
        db_controller.add_wiki_info(id_disease, wiki_info[0], wiki_info[1], wiki_info[2])
    return result


def _add_disease_and_codes(disease_name: str, icd10_code: str, icd11_code: str):
    db_controller.add_disease_entry(disease_name)
    id_disease: int = db_controller.get_disease_id_by_name(disease_name)
    db_controller.add_icd_codes(id_disease, icd10_code, icd11_code)


def _process_icd10_code(icd10_code: str, additional_languages: list, icd_mapper, wikipedia_mapper) -> dict:
    result: dict = {}
    icd11_code: str = icd_mapper.icd_10_to_icd_11(icd10_code)
    if icd11_code == "":
        return {}
    result['icd11_code'] = icd11_code

    disease_name: str = icd_mapper.get_icd_10_name(icd10_code)
    wiki_infos: list = wikipedia_mapper.get_disease_wikipedia_data(icd10_code, additional_languages)
    result['disease_name'] = disease_name
    result['wiki_infos'] = wiki_infos
    result['relations'] = icd_mapper.get_icd_10_relations(icd10_code)

    found_languages: list = []
    for wiki_info in wiki_infos:
        found_languages.append(wiki_info[0])
    result['found_languages'] = found_languages

    result['not_found_languages'] = []
    for additional_language in additional_languages:
        if additional_language not in found_languages:
            result['not_found_languages'].append(additional_language)
    return result


def get_icd10(request, code: str):
    db_connection = _check_database_connection()
    if db_connection.status_code != 0:
        return db_connection
    if not db_controller.get_disease_id_by_icd10(code):
        return Response(status=404)

    response_format: str = request.args.get('format')

    result: list = db_controller.get_icd10_info(code)

    if not result:
        return Response(status=404)

    if response_format == "json-pretty":
        return Response(response=json.dumps(result, indent=3), status=200, mimetype='application/json')
    else:
        return Response(response=json.dumps(result), status=200, mimetype='application/json')


def get_icd11(request, code: str):
    db_connection = _check_database_connection()
    if db_connection.status_code != 0:
        return db_connection
    if not db_controller.get_disease_id_by_icd11(code):
        return Response(status=404)

    response_format: str = request.args.get('format')
    result: list = db_controller.get_icd11_info(code)

    if not result:
        return Response(status=404)

    if response_format == "json-pretty":
        return Response(response=json.dumps(result, indent=3), status=200, mimetype='application/json')
    else:
        return Response(response=json.dumps(result), status=200, mimetype='application/json')


def get_disease(request, id_disease: int):
    db_connection = _check_database_connection()
    if db_connection.status_code != 0:
        return db_connection

    response_format: str = request.args.get('format')
    result: list = db_controller.get_disease_info([id_disease])
    if not result:
        return Response(status=404)

    if response_format == "json-pretty":
        return Response(response=json.dumps(result, indent=3), status=200, mimetype='application/json')
    else:
        return Response(response=json.dumps(result), status=200, mimetype='application/json')


def add_additional_info(request) -> Response:
    db_connection = _check_database_connection()
    if db_connection.status_code != 0:
        return db_connection

    data: dict = request.get_json()

    if not {'diseaseId', 'type', 'author', 'info'} <= request.get_json().keys():
        return Response(status=400)

    db_controller.add_additional_info(data['diseaseId'], data['type'], data['author'], data['info'])
    return Response(status=201)


def modify_additional_info(request) -> Response:
    db_connection = _check_database_connection()
    if db_connection.status_code != 0:
        return db_connection

    data: dict = request.get_json()

    if not {'infoId', 'type', 'author', 'info'} <= request.get_json().keys():
        return Response(status=400)

    db_controller.modify_additional_info(data['infoId'], data['type'], data['author'], data['info'])
    return Response(status=201)


def delete_additional_info(id_disease: int) -> Response:
    db_connection = _check_database_connection()
    if db_connection.status_code != 0:
        return db_connection

    db_controller.delete_additional_info(id_disease)
    return Response(status=200)
