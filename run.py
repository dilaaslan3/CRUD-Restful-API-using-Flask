import copy
import decimal
import jsonschema
from bson.errors import InvalidId
from flask import Flask, request, Response
import datetime
import json
import pymongo
from flask_jsonschema_validator import JSONSchemaValidator
from bson import ObjectId
from bson.json_util import default
import logging

app = Flask(__name__)

JSONSchemaValidator(app=app, root="schemas")

db = pymongo.MongoClient(host='mongodb://localhost:32768/dila_test').get_default_database()


def bson_to_json(o):
    if isinstance(o, ObjectId):
        return str(o)
    if isinstance(o, datetime.datetime):
        r = o.isoformat()
        return r + 'Z'
    elif isinstance(o, datetime.date):
        return o.isoformat()
    elif isinstance(o, datetime.time):
        r = o.isoformat()
        if o.microsecond:
            r = r[:12]
        return r
    elif isinstance(o, decimal.Decimal):
        return str(o)
    return default(o)


@app.route('/api/v1/posts', methods=['POST'])
@app.validate('posts', 'create')
def create_post():
    body = request.json

    title = body["title"]

    exist_document = db.posts.find_one({
        "title": title,
        "is_active": True,
        "status": "active"
    })

    if exist_document:
        return Response(json.dumps({
            'err_msg': 'Resource already exist in db with title: <{}>'.format(title),
            'err_code': 'errors.duplicateRecord'
        }), mimetype='application/json', status=409)

    body['sys'] = {
        'created_at': datetime.datetime.utcnow(),
        'created_by': 'system'
    }
    db.posts.insert_one(body)

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
        return Response(json.dumps({
            'err_msg': 'Provided id is not valid ObjectId, please provide valid ObjectId',
            'err_code': 'errors.badRequest'
        }), mimetype='application/json', status=400)

    exist_document = db.posts.find_one({
        '_id': doc_id_as_obj_id
    })

    if not exist_document:
        return Response(json.dumps({
            'err_msg': 'Document not found by given id: <{}>'.format(document_id),
            'err_code': 'errors.notFound'
        }), mimetype='application/json', status=404)

    return Response(json.dumps(exist_document, default=bson_to_json), mimetype='application/json', status=200)


@app.route('/api/v1/posts/<document_id>', methods=['DELETE'])
def delete_post(document_id):
    """if the document exists then delete it"""
    try:
        doc_id_as_obj_id = ObjectId(document_id)
    except InvalidId as ex:
        return Response(json.dumps({
            'err_msg': 'Provided id is not valid ObjectId, please provide valid ObjectId',
            'err_code': 'errors.badRequest'
        }), mimetype='application/json', status=400)

    exist_document = db.posts.find_one({
        '_id': doc_id_as_obj_id
    })
    if not exist_document:
        return Response(json.dumps({
            'err_msg': 'Document not found by given id: <{}>'.format(document_id),
            'err_code': 'errors.notFound'
        }), mimetype='application/json', status=404)

    # my_col = db["posts"]
    # my_col.delete_one(exist_document)
    db.posts.delete_one({
        '_id': doc_id_as_obj_id
    })
    return Response(json.dumps({}), status=204)


@app.route('/api/v1/posts/<document_id>', methods=['PUT'])
@app.validate('posts', 'update')
def update_post(document_id):
    body = request.json

    try:
        doc_id_as_obj_id = ObjectId(document_id)
    except InvalidId as ex:
        return Response(json.dumps({
            'err_msg': 'Provided id is not valid ObjectId, please provide valid ObjectId',
            'err_code': 'errors.badRequest'
        }), mimetype='application/json', status=400)

    exist_document = db.posts.find_one({
        '_id': doc_id_as_obj_id
    })
    if not exist_document:
        return Response(json.dumps({
            'err_msg': 'Document not found by given id: <{}>'.format(document_id),
            'err_code': 'errors.notFound'
        }), mimetype='application/json', status=404)

    exist_document.pop("_id")
    current_sys = exist_document.pop("sys")

    old_exist_document = copy.deepcopy(exist_document)
    exist_document.update(body)

    if old_exist_document == exist_document:
        return Response(json.dumps({
            'err_msg': 'Document already same as the exist document',
            'err_code': 'errors.identicalDocumentError'
        }), mimetype='application/json', status=409)

    current_sys["modified_at"] = datetime.datetime.utcnow()
    current_sys["modified_by"] = "system"

    exist_document["sys"] = current_sys

    db.posts.update_one({
        '_id': doc_id_as_obj_id
    }, {
        "$set": exist_document
    })

    exist_document["_id"] = document_id

    return Response(json.dumps(exist_document, default=bson_to_json), mimetype='application/json', status=200)


@app.route('/api/v1/posts/_query', methods=['POST'])
@app.validate('posts', 'query')
def query_post():
    body = request.json
    limit = int(request.args.get("limit", 200))
    skip = int(request.args.get("skip", 0))

    if limit > 200:
        limit = 200
    where = body.get("where", {})
    select = body.get("select", {})  # selecti bulamazsa body de boş obje dön

    if not select:
        document_cursor = db.posts.find(where)
    else:
        values = select.values()
        unique_values = set(values)

        if len(unique_values) != 1:
            return Response(json.dumps({
                'err_msg': 'Projection cannot have a mix of inclusion and exclusion.',
                'err_code': 'errors.badRequest'
            }), mimetype='application/json', status=400)
        document_cursor = db.posts.find(where, select)

    document_cursor.limit(limit)
    document_cursor.skip(skip)

    documents = list(document_cursor)
    envelop = {
        "data": {
            "items": documents,
            "count": len(documents)
        }
    }

    return Response(json.dumps(envelop, default=bson_to_json), mimetype='application/json', status=200)


@app.errorhandler(jsonschema.ValidationError)
def onValidationError(e):
    return Response(json.dumps({
        'err_msg': e.message,
        'err_code': 'errors.validationError'
    }), mimetype='application/json', status=400)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
