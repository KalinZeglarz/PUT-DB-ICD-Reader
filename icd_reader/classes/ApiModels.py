from flask_restplus import fields


class ApiModels:
    """
    Model container class
    """
    db_table = None
    user_login = None

    def __init__(self, api):
        self.map_post_put_body = api.model('Map', {
            'data': fields.List(required=True, cls_or_instance=fields.String)
        })
        self.additional_info_post_body = api.model('Additional info (add)', {
            'diseaseId': fields.Integer,
            'type': fields.String,
            'author': fields.String,
            'info': fields.String,
        })
        self.additional_info_put_body = api.model('Additional info (modify)', {
            'infoId': fields.Integer,
            'type': fields.String,
            'author': fields.String,
            'info': fields.String,
        })
