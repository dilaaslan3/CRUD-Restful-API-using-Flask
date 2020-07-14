from functools import wraps

from flask import request
from jsonschema import validate, ValidationError

from plugins.errors import DilaError


def validate_by(schema):
    def decorator(f):
        @wraps(f)
        def validate_by_schema(*args, **kwargs):
            try:
                body = request.json
                validate(body, schema)
            except ValidationError as e:
                raise DilaError(
                    err_msg=e.message,
                    err_code="errors.validationError",
                    status_code=400
                )
            response = f(*args, **kwargs)
            return response
        return validate_by_schema
    return decorator
