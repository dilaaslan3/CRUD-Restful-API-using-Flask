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
@app.validate('posts',
              'create')  # hangi resource için bunu yapıyoruz ve dosyanın adı ile aynı olmalı, par2 => o dosya için hnagi schemayı kullancağız
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


@app.errorhandler(jsonschema.ValidationError)
def onValidationError(e):
    return Response(json.dumps({
        'err_msg': e.message,
        'err_code': 'errors.validationError'
    }), mimetype='application/json', status=400)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
