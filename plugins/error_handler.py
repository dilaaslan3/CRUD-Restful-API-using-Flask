import json
import jsonschema
from flask import Response
from plugins.errors import DilaError
from src.helpers.json_helpers import bson_to_json


def init_error_handler(app):
    @app.errorhandler(jsonschema.ValidationError) #soru8: bu da bir decorator anladığım kadarıyla, kullanımı kesin olarak bu şekilde mi hangi durumlarda ihtiyaç duyarım ve başka ne tür decoratorlar vardır ve tam olarak decorator ne iş yapar
    def onValidationError(e):
        return Response(json.dumps({
            'err_msg': e.message,
            'err_code': 'errors.validationError'
        }), mimetype='application/json', status=400)

    @app.errorhandler(Exception) #soru9: 9. satırdaki aynı decoratorı? burda farkli bir parametre ile çalıştırdık neden Exception ile çalıştırdık?
    def handleError(error): #soru10: error parametresi bize nerden ne şekilde nasıl dönüyor
        if isinstance(error, DilaError):
            response = {
                "err_msg": error.err_msg,
                "err_code": error.err_code
            }
            status_code = error.status_code
        else:
            response = {
                "err_msg": "An error occured.",
                "err_code": "errors.internalServerError"
            }
            status_code = 500

        return Response(json.dumps(response, default=bson_to_json), mimetype='application/json', status=status_code)
