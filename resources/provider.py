from flask_restful import Resource, reqparse
from bson import json_util
from bson.objectid import ObjectId
from flask_jwt_extended import (
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
)

from db import mongo


class ProviderRegister(Resource):
    def post(self):
        pass


class Provider(Resource):
    def get(self, id):
        pass

    def delete(self, id):
        pass


class ProviderList(Resource):
    def get(self):
        pass
