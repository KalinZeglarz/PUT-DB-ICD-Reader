from flask_restplus import fields


class ApiModels:
    """
    Model container class
    """
    db_table = None
    user_login = None

    def __init__(self, api):
        self.map_request_body = api.model('Map request', {
            'data': fields.List(required=True, cls_or_instance=fields.String)
        })
