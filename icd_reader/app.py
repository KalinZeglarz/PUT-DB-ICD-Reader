import flask_restplus
from flask import Flask, request
from flask_restplus import Resource

from icd_reader import logger
from icd_reader.classes import ApiController
from icd_reader.classes.ApiModels import ApiModels

logger.initialize()

app = Flask(__name__)
api = flask_restplus.Api(app, version='1.0', title='ICD READER API', description='An API for ICD READER')
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
        return ApiController.add_or_update_icd10(request)

    def put(self):
        return ApiController.add_or_update_icd10(request)


@ns_reader.route('/icd-10/<code>')
@ns_reader.doc(params={'code': 'An ICD-10 code'})
@ns_reader.response(200, 'Success')
@ns_reader.response(404, 'Not Found')
@ns_reader.response(500, 'Internal Server Error')
class GetIcd10(Resource):
    @ns_reader.doc(params={'format': 'Response data format (json, json-pretty)'})
    def get(self, code: str):
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
        return ApiController.get_disease(request, id)


@ns_additional_info.route('/')
@ns_additional_info.response(201, 'Created')
@ns_additional_info.response(400, 'Bad Request')
@ns_additional_info.response(500, 'Internal Server Error')
class AdditionalInfo(Resource):
    @ns_additional_info.expect(models.additional_info_post_body)
    def post(self):
        return ApiController.add_additional_info(request)

    @ns_additional_info.expect(models.additional_info_put_body)
    def put(self):
        return ApiController.modify_additional_info(request)


@ns_additional_info.route('/<id>')
@ns_additional_info.response(200, 'Success')
@ns_additional_info.response(500, 'Internal Server Error')
class AdditionalInfo(Resource):
    def delete(self, id: int):
        return ApiController.delete_additional_info(id)


if __name__ == '__main__':
    ApiController.load_configuration()
    app.run(
        host='0.0.0.0',
        port=80
    )
