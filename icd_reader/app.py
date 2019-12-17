import json
import logging

from flask import Flask, request, Response
from flask_restplus import Resource, Api

from icd_reader import logger
from icd_reader.classes.DbController import DbController
from icd_reader.classes.IcdMapper import IcdMapper
from icd_reader.classes.IcdWikipediaMapper import IcdWikipediaMapper
from icd_reader.classes.MySqlController import MySqlController

logger.initialize()

app = Flask(__name__)
api = Api(app, version='1.0', title='ICD READER API',
          description='An API for ICD READER')
ns_reader = api.namespace('icd-reader', description='')

icd_mapper: IcdMapper

db_controller: DbController

wikipedia_mapper: IcdWikipediaMapper


def _load_configuration():
    global icd_mapper
    global db_controller
    global wikipedia_mapper

    with open('resources/configuration.json', 'r') as f:
        configuration = json.load(f)
        logging.info("Loaded configuration from path 'resources/configuration.json'")
    db_controller = MySqlController(
        host=configuration['db-parameters']['host'],
        user=configuration['db-parameters']['user'],
        password=configuration['db-parameters']['password']
    )
    icd_mapper = IcdMapper(
        client_id=configuration['icd-api-credentials']['client-id'],
        client_secret=configuration['icd-api-credentials']['client-secret']
    )
    wikipedia_mapper = IcdWikipediaMapper("resources/codeSpaces.json")


@ns_reader.route('/')
def icd_reader():
    return 'This is ICD Reader'


# noinspection DuplicatedCode
@ns_reader.route('/map/icd-10', methods=['POST', 'PUT'])
def add_or_update():
    global icd_mapper
    global db_controller
    global wikipedia_mapper

    input_data: list = request.get_json()['data']
    for icd10_code in input_data:
        icd11_code: str = icd_mapper.icd_10_to_icd_11(icd10_code)
        disease_name: str = icd_mapper.get_icd_10_name(icd10_code)
        eng_title, eng_url, pol_url = wikipedia_mapper.get_disease_wikipedia_data(icd10_code)
        db_controller.add_disease_entry(disease_name)
        id_disease: int = db_controller.get_disease_id_by_name(disease_name)
        db_controller.add_icd_codes(id_disease, icd_mapper.split_icd_10_code(icd10_code), icd11_code)
        db_controller.add_wiki_info(id_disease, 'eng', eng_title, eng_url)
        db_controller.add_wiki_info(id_disease, 'pol', '', pol_url)
    return Response(status=201)


# noinspection DuplicatedCode
@ns_reader.route('/icd-10/<code>', methods=['GET'])
def get_icd10(code: str):
    response_format: str = request.args.get('format')
    result: dict = db_controller.get_icd_10_info(code)
    if response_format == "html":
        return Response("<h1>Not implemented yet!</h1>", status=200, mimetype='text/html')
    if response_format == "json-pretty":
        return Response(response=json.dumps(result, indent=3), status=200, mimetype='application/json')
    else:
        return Response(response=json.dumps(result), status=200, mimetype='application/json')


# noinspection DuplicatedCode
@ns_reader.route('/icd-11/<code>', methods=['GET'])
def get_icd11(code: str):
    response_format: str = request.args.get('format')
    result: dict = db_controller.get_icd_11_info(code)
    if response_format == "html":
        return Response("<h1>Not implemented yet!</h1>", status=200, mimetype='text/html')
    if response_format == "json-pretty":
        return Response(response=json.dumps(result, indent=3), status=200, mimetype='application/json')
    else:
        return Response(response=json.dumps(result), status=200, mimetype='application/json')


if __name__ == '__main__':
    _load_configuration()
    app.run(
        host='0.0.0.0',
        port=80
    )
