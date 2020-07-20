import copy
from datetime import datetime

from bson import ObjectId
from flask import request

from plugins.errors import DilaError


class PostService(
    object):  # bir class bir yerden inherit ediliyorsa bu parametre olarak classa verilir ama hiçbir yerden inherit edilmiyorsa parametre olarak object verilir
    def __init__(self,
                 db):  # classımızın constructorıdır ilk parametresi mutlaka self olmalıdır, ikinci parametre olarak db yi verdik çünkü bu classın yapacağı iş dbye gitmek
        self.db = db

    def get_post(self, post_id, raise_exception=False):
        document = self.db.posts.find_one({
            "_id": ObjectId(post_id)
        })
        if raise_exception and not document:
            raise DilaError(
                err_msg="Document not found by given id: <{}>, in collection: <{}>".format(post_id, "posts"),
                err_code="errors.resourceNotFound",
                status_code=404
            )
        return document

    def create_post(self, raise_exception=False):
        body = request.json
        title = body["title"]

        document = self.db.posts.find_one({
            "title": title,
            "is_active": True,
            "status": "active"
        })

        if raise_exception and document:
            raise DilaError(
                err_msg='Resource already exist in db with title: <{}>'.format(title),
                err_code='errors.duplicateRecord',
                status_code=409
            )

        body['sys'] = {
            'created_at': datetime.utcnow(),
            'created_by': 'system'
        }
        _ = self.db.posts.insert_one(body)

        return body

    def delete_post(self, post_id, raise_exception=False):
        _ = self.get_post(post_id, raise_exception=raise_exception)
        self.db.posts.delete_one({
            "_id": ObjectId(post_id)
        })

    def update_post(self, post_id, raise_exception=False):
        body = request.json
        document = self.db.posts.find_one({
            '_id': ObjectId(post_id)
        })
        if raise_exception and not document:
            raise DilaError(
                err_msg="Document not found by given id: <{}>, in collection: <{}>".format(post_id, "posts"),
                err_code="errors.resourceNotFound",
                status_code=404
            )
        document.pop("_id")
        current_sys = document.pop("sys")

        old_document = copy.deepcopy(document)
        document.update(body)

        if old_document == document:
            raise DilaError(
                err_msg="Document already same as the exist document",
                err_code="identicalDocumentError",
                status_code=409
            )
        current_sys["modified_at"] = datetime.utcnow()
        current_sys["modified_by"] = "system"

        document["sys"] = current_sys

        self.db.posts.update_one({
            '_id': ObjectId(post_id)
        }, {
            "$set": document
        })
        document["_id"] = post_id

        return document

    # def query_post(self, where, raise_exception=False):
