import pymongo
from flask import Flask
from plugins.error_handler import init_error_handler
from src.api.post import init_post_api
from src.services.post_service import PostService


def create_app(): #soru4: neden bir sürü _init__.py dosyası var ve neden create_app methodunu buradakinde tanımladık
    app = Flask(__name__) #soru1: neden Flask(__name__) yazdık bir flask application başlatmanın yolu bu mudur?
    db = pymongo.MongoClient(host='mongodb://localhost:32768/dila_test').get_default_database() #soru2: neden db ye post_services in içinde ulaşmka yerine buradan erişiyoruz
    app.db = db #soru3: neden app.db diyoruz bu bir kural mı bu şekilde mi db mizi app e bağlıyoruz
    app.post_service = PostService(db) #soru5: neden PostService methodumuzdan dönen değeri app.post_service attık, sanırım bu satırı ve posts.py daki 58. satırı anlamamışım
    init_post_api(app)  #soru7:neden bu ve bir alttaki satırdaki methodlarımız app i parametre olarak alıyorlar
    init_error_handler(app)
    return app
