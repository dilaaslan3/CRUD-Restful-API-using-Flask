import pymongo
from flask import Flask
from plugins.error_handler import init_error_handler
from src.api.post import init_post_api
from src.services.post_service import PostService


def create_app():
    app = Flask(__name__)
    db = pymongo.MongoClient(host='mongodb://localhost:32768/dila_test').get_default_database()
    app.post_service = PostService(db)
    init_post_api(app)
    init_error_handler(app)
    return app
