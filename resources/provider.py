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


_provider_parser = reqparse.RequestParser()
_provider_parser.add_argument(
    "name", type=str, required=True, help="This field cannot be blank."
)
_provider_parser.add_argument(
    "location", type=str, required=True, help="This field cannot be blank."
)


class ProviderRegister(Resource):
    def post(self):
        data = _provider_parser.parse_args()

        try:
            provider = mongo.db.providers.find_one(
                {"name": data["name"]})
        except:
            return {"message": "An error occurred looking up the provider"}, 500

        if provider:
            return {"message": "A provider with that username already exists"}, 400

        try:
            mongo.db.providers.insert_one(
                {"name": data["name"], "location": data["location"]}
            )

            return {"message": "provider created successfully."}, 201
        except:
            return {"message": "An error occurred creating the provider"}, 500


class Provider(Resource):
    def get(self, _id):
        try:
            provider = mongo.db.providers.find_one({"_id": ObjectId(_id)})
        except:
            return {"message": "An error occurred looking up the provider"}, 500

        if provider:
            return json_util._json_convert(provider), 200
        return {"message": "provider not found"}, 404

    def delete(self, _id):
        try:
            provider = mongo.db.providers.find_one({"_id": ObjectId(_id)})
        except:
            return {"message": "An error occurred trying to look up this provider"}, 500

        if provider:
            try:
                mongo.db.providers.delete_one({"_id": ObjectId(_id)})
            except:
                return {"message": "An error occurred trying to delete this provider"}, 500
            return {"message": "provider was deleted"}, 200
        return {"message": "provider not found"}, 404


class ProviderList(Resource):
    def get(self):
        try:
            providers = mongo.db.providers.find()
        except:
            return {"message": "An error occurred looking up all of the providers"}, 500

        if providers.count():
            return {"providers": json_util._json_convert(providers)}, 200
        return {"message": "No providers were found"}, 404
