# -*- coding: utf-8 -*-

import functools
import json
import logging
import os

from flask import request

from jsonschema import validate

logger = logging.getLogger( __name__ )


class JSONSchemaValidatorException( Exception ):
    pass


class JSONSchemaValidator( object ):
    def __init__( self, app, root=None ):
        self.app = app
        self.root = root
        self.cache = { }

        if self.root is None:
            self.root = os.path.join( os.path.dirname( os.getcwd() ), "schemas" )

        self.init_app( app, root )

    def init_app( self, app, root=None ):
        app.extensions[ 'jsonschemavalidator' ] = self
        app.validate = self.validate

    def get_schema( self, kind, operation='default' ):
        if kind not in self.cache:
            try:
                path = os.path.join( self.root, '{0}.json'.format( kind ) )
                logger.info( 'Reading schema from {0}'.format( path ) )
                with open( path ) as file:
                    schema = json.load( file )
                    self.cache[ kind ] = schema
            except:
                self.cache[ kind ] = { }

        return self.cache[ kind ].get( operation )

    def validate( self, kind, operation='default', root=None ):
        def wrapper( func ):
            @functools.wraps( func )
            def decorated( *args, **kwargs ):
                schema = self.get_schema( kind, operation )
                if schema is None:
                    raise JSONSchemaValidatorException( "The validation schema kind or operation could not be found" )
                validate( request.json, schema )
                return func( *args, **kwargs )

            return decorated

        return wrapper
