import json
import jsonschema
from flask import Response
from plugins.errors import DilaError
from src.helpers.json_helpers import bson_to_json


def init_error_handler(app):
    @app.errorhandler(jsonschema.ValidationError)
    def onValidationError(e):
        return Response(json.dumps({
            'err_msg': e.message,
            'err_code': 'errors.validationError'
        }), mimetype='application/json', status=400)

    @app.errorhandler(Exception)
    def handleError(error):
        if isinstance(error, DilaError):
            response = {
                "err_msg": error.err_msg,
                "err_code": error.err_code
            }
            status_code = error.status_code
        else:
            response = {
                "err_msg": "An error occurred.",
                "err_code": "errors.internalServerError"
            }
            status_code = 500

        return Response(json.dumps(response, default=bson_to_json), mimetype='application/json', status=status_code)
