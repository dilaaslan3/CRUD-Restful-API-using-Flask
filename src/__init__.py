import pymongo
from flask import Flask
from flask_jsonschema_validator import JSONSchemaValidator

from plugins.error_handler import init_error_handler
from src.api.post import init_post_api


def create_app():
    app = Flask(__name__)
    JSONSchemaValidator(app=app, root="schemas")
    db = pymongo.MongoClient(host='mongodb://localhost:32768/dila_test').get_default_database()
    app.db = db
    init_post_api(app)
    init_error_handler(app)
    return app
