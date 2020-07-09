import unittest

import json
import os
import os.path
from flask import Flask, request, jsonify
from flask_jsonschema_validator import JSONSchemaValidator


class TestFlaskJsonschemaValidatorCase( unittest.TestCase ):

    def setUp( self ):
        app = Flask( __name__ )
        root = os.path.join( os.path.dirname( __file__ ), "schemas" )
        JSONSchemaValidator( app=app, root=root )
        app.config[ 'TESTING' ] = True
        client = app.test_client()
        self.app = app
        self.client = client

    def testExampleCode( self ):
        # Define application route
        @self.app.route( '/register', methods=[ 'POST' ] )
        @self.app.validate( 'users', 'register' )
        def routeRegister():
            user = request.json
            return jsonify( user )

        # Define POST data
        post_data = {
            "name":     "fred",
            "email":    "fred@foo.com",
            "password": "frediscool"
        }

        # Invoke request as if transmitted by HTTP client
        # Slightly modified syntax (json.dumps and content_type specified) to make this work in
        # Flask's test client context
        self.client.post( '/register', data = json.dumps( post_data ), content_type = 'application/json' )



if __name__ == '__main__':
    unittest.main()
