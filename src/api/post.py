import copy
import datetime
import json
import pymongo
from bson import ObjectId
from bson.errors import InvalidId
from flask import request, Response
from plugins.errors import DilaError
from plugins.validator import validate_by
from src.helpers.json_helpers import bson_to_json
from src.schemas.posts import POST_SCHEMA


def init_post_api(app):
    @app.route('/api/v1/posts', methods=['POST'])
    @validate_by(POST_SCHEMA["create"])
    def create_post():
        # body = request.json
        #
        # title = body["title"]
        #
        # exist_document = app.db.posts.find_one({
        #     "title": title,
        #     "is_active": True,
        #     "status": "active"
        # })
        #
        # if exist_document:
        #     raise DilaError(
        #         err_msg='Resource already exist in db with title: <{}>'.format(title),
        #         err_code='errors.duplicateRecord',
        #         status_code=409
        #     )
        #
        # body['sys'] = {
        #     'created_at': datetime.datetime.utcnow(),
        #     'created_by': 'system'
        # }
        # app.db.posts.insert_one(body)

        body = app.post_service.create_post(raise_exception=True)

        return Response(
            json.dumps(body, default=bson_to_json),
            mimetype='application/json',
            status=201
        )

    @app.route('/api/v1/posts/<document_id>', methods=['GET'])
    def get_post(document_id):
        try:
            doc_id_as_obj_id = ObjectId(document_id)
        except InvalidId as ex:
            raise DilaError(
                err_msg='Provided id is not valid ObjectId, please provide valid ObjectId',
                err_code='errors.badRequest',
                status_code=400
            )

        exist_document = app.post_service.get_post(doc_id_as_obj_id, raise_exception=True)  # soru6: ??

        return Response(json.dumps(exist_document, default=bson_to_json), mimetype='application/json', status=200)

    @app.route('/api/v1/posts/<document_id>', methods=['DELETE'])
    def delete_post(document_id):
        """burada sadece gelen doucment_id li bir document var mı kontrolü yapılır,"""
        """validasyon işlemleri burada, database e erişme ve silme işlemleri post_service in içindeki delete_post ta gerçekleştirilir."""
        try:
            doc_id_as_obj_id = ObjectId(document_id)
        except InvalidId as ex:
            raise DilaError(
                err_msg='Provided id is not valid ObjectId, please provide valid ObjectId',
                err_code='errors.badRequest',
                status_code=400
            )

        # exist_document = app.db.posts.find_one({
        #     '_id': doc_id_as_obj_id
        # })
        # if not exist_document:
        #     raise DilaError(
        #         err_msg='Document not found by given id: <{}>'.format(document_id),
        #         err_code='errors.notFound',
        #         status_code=404
        #     )
        #
        app.post_service.delete_post(doc_id_as_obj_id, raise_exception=True)
        return Response(json.dumps({}), status=204)

    @app.route('/api/v1/posts/<document_id>', methods=['PUT'])
    @validate_by(POST_SCHEMA["update"])
    def update_post(document_id):
        body = request.json

        try:
            doc_id_as_obj_id = ObjectId(document_id)
        except InvalidId as ex:
            raise DilaError(
                err_msg='Provided id is not valid ObjectId, please provide valid ObjectId',
                err_code='errors.badRequest',
                status_code=400
            )

        exist_document = app.db.posts.find_one({
            '_id': doc_id_as_obj_id
        })
        if not exist_document:
            raise DilaError(
                err_msg='Document not found by given id: <{}>'.format(document_id),
                err_code='errors.notFound',
                status_code=404
            )

        exist_document.pop("_id")
        current_sys = exist_document.pop("sys")

        old_exist_document = copy.deepcopy(exist_document)
        exist_document.update(body)

        if old_exist_document == exist_document:
            raise DilaError(
                err_msg='Document already same as the exist document',
                err_code='errors.identicalDocumentError',
                status_code=409
            )

        current_sys["modified_at"] = datetime.datetime.utcnow()
        current_sys["modified_by"] = "system"

        exist_document["sys"] = current_sys

        app.db.posts.update_one({
            '_id': doc_id_as_obj_id
        }, {
            "$set": exist_document
        })

        exist_document["_id"] = document_id

        return Response(json.dumps(exist_document, default=bson_to_json), mimetype='application/json', status=200)

    @app.route('/api/v1/posts/_query', methods=['POST'])
    @validate_by(POST_SCHEMA["query"])
    def query_post():
        """
        postları sorgulamak/filtrelemek için kullanılır
        kullanıcıdan where select limit skip sort parametreleri istenir
        bütün parametreler valide edilir

            request.args.get(parameter, 0))  #default değeri null değil de 0 olsun diye 0 set ettik
            select = body.get("select", {})  # selecti bulamazsa body de boş obje dön

        :return: envelop => data: {items: [], count: 0}
        """
        body = request.json
        raw_parameters = ["limit", "skip"]
        parameters = {}
        for parameter in raw_parameters:
            try:
                parameters[parameter] = int(
                    request.args.get(parameter, 0))
            except ValueError:
                raise DilaError(
                    err_msg="{} parameter must be an integer. Provided value: {}".format(
                        parameter,
                        request.args.get(parameter)
                    ),
                    err_code='errors.badRequest',
                    status_code=400
                )

        limit = parameters.get("limit")
        skip = parameters.get("skip")

        sort_field = request.args.get("sort_field")
        sort_by = request.args.get("sort_by", "desc")

        if not limit and limit > 200:
            limit = 200
        where = body.get("where", {})
        select = body.get("select", {})

        if not select:
            document_cursor = app.db.posts.find(where)
        else:
            values = select.values()
            unique_values = set(values)

            if len(unique_values) != 1:
                raise DilaError(
                    err_msg='Projection cannot have a mix of inclusion and exclusion.',
                    err_code='errors.badRequest',
                    status_code=400
                )
            document_cursor = app.db.posts.find(where, select)

        document_cursor.limit(limit)
        document_cursor.skip(skip)

        if sort_field:
            if sort_by == "asc":
                sort_by = pymongo.ASCENDING
            elif sort_by == "desc":
                sort_by = pymongo.DESCENDING
            else:
                raise DilaError(
                    err_msg='Please provide valid sort_by field: asc, desc.',
                    err_code='errors.badRequest',
                    status_code=400
                )
            document_cursor.sort([(sort_field, sort_by)])

        documents = list(document_cursor)
        envelop = {
            "data": {
                "items": documents,
                "count": len(documents)
            }
        }

        return Response(json.dumps(envelop, default=bson_to_json), mimetype='application/json', status=200)
