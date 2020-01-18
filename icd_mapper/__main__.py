import os

import flask_restplus
from flask import Flask, request
from flask_restplus import Resource

from icd_mapper import logger
from icd_mapper.classes import ApiController
from icd_mapper.classes.ApiModels import ApiModels

logger.initialize()

api_description: str = 'ICD Mapper API is a REST API that allows mapping ICD-10 codes to ICD-11 codes and gathering ' \
                       'disease related Wikipedia articles'

app = Flask(__name__)
api = flask_restplus.Api(app, version='1.0', title='ICD READER API', description=api_description)
ns_reader = api.namespace('icd-reader', description='')
ns_additional_info = api.namespace('icd-reader/additional-info', description='')

models: ApiModels = ApiModels(api)


@ns_reader.route('/map/icd-10')
@ns_reader.expect(models.map_post_put_body)
@ns_reader.response(201, 'Created')
@ns_reader.response(400, 'Bad Request')
@ns_reader.response(500, 'Internal Server Error')
class MapIcd10(Resource):

    def post(self):
        """This endpoint maps given ICD-10 codes to ICD-11 codes and find Wikipedia articles."""
        return ApiController.add_or_update_icd10(request)

    def put(self):
        """Alias to POST endpoint."""
        return ApiController.add_or_update_icd10(request)


@ns_reader.route('/icd-10/<code>')
@ns_reader.doc(params={'code': 'An ICD-10 code'})
@ns_reader.response(200, 'Success')
@ns_reader.response(404, 'Not Found')
@ns_reader.response(500, 'Internal Server Error')
class GetIcd10(Resource):
    @ns_reader.doc(params={'format': 'Response data format (json, json-pretty)'})
    def get(self, code: str):
        """This endpoint returns all information about diseases matching ICD-10 codes."""
        return ApiController.get_icd10(request, code)


# noinspection DuplicatedCode
@ns_reader.route('/icd-11/<code>')
@ns_reader.doc(params={'code': 'An ICD-11 code'})
@ns_reader.response(200, 'Success')
@ns_reader.response(404, 'Not Found')
@ns_reader.response(500, 'Internal Server Error')
class GetIcd11(Resource):
    @ns_reader.doc(params={'format': 'Response data format (json, json-pretty)'})
    def get(self, code: str):
        """This endpoint returns all information about disease matching ICD-11 code."""
        return ApiController.get_icd11(request, code)


# noinspection DuplicatedCode
@ns_reader.route('/disease/<id>')
@ns_reader.doc(params={'id': 'Internal disease ID'})
@ns_reader.response(200, 'Success')
@ns_reader.response(404, 'Not Found')
@ns_reader.response(500, 'Internal Server Error')
class GetDisease(Resource):
    @ns_reader.doc(params={'format': 'Response data format (json, json-pretty)'})
    def get(self, id: int):
        """This endpoint returns all information about disease matching database id."""
        return ApiController.get_disease(request, id)


@ns_additional_info.route('/')
@ns_additional_info.response(201, 'Created')
@ns_additional_info.response(400, 'Bad Request')
@ns_additional_info.response(500, 'Internal Server Error')
class AdditionalInfo(Resource):
    @ns_additional_info.expect(models.additional_info_post_body)
    def post(self):
        """This endpoint adds additional info to disease with given database id."""
        return ApiController.add_additional_info(request)

    @ns_additional_info.expect(models.additional_info_put_body)
    def put(self):
        """This endpoint modifies additional info with given database id."""
        return ApiController.modify_additional_info(request)


@ns_additional_info.route('/<id>')
@ns_additional_info.response(200, 'Success')
@ns_additional_info.response(500, 'Internal Server Error')
class AdditionalInfo(Resource):
    def delete(self, id: int):
        """This endpoint deletes additional info with given database id."""
        return ApiController.delete_additional_info(id)


if __name__ == '__main__':
    # Sets working directory to this script's directory
    abs_path = os.path.abspath(__file__)
    dir_name = os.path.dirname(abs_path)
    os.chdir(dir_name)

    ApiController.load_configuration()
    app.run(
        host=str(os.getenv('server_host', '0.0.0.0')),
        port=int(os.getenv('server_port', 5000))
    )
