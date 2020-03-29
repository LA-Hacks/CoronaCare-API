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

_resource_parser = reqparse.RequestParser()
_resource_parser.add_argument(
    "name", type=str, required=True, help="This field cannot be blank."
)
_resource_parser.add_argument(
    "standard", type=list, action="append", location="json", required=True, help="This field cannot be blank."
)


class ResourceRegister(Resource):
    def post(self):
        data = _resource_parser.parse_args()

        try:
            resource = mongo.db.resources.find_one(
                {"name": data["name"]})
        except:
            return {"message": "An error occurred looking up the name"}, 500

        if resource:
            return {"message": "Resource has already been specified"}, 400

        try:
            mongo.db.resources.insert_one(
                {"name": data["name"], "standard": [
                    "".join([ch for ch in str_lst]) for str_lst in data["standard"]]}
            )

            return {"message": "Resource created successfully."}, 201
        except:
            return {"message": "An error occurred creating the Resource"}, 500


class Resource(Resource):
    def get(self, _id):
        try:
            resource = mongo.db.resources.find_one({"_id": ObjectId(_id)})
        except:
            return {"message": "An error occurred looking up the Resource"}, 500

        if Resource:
            return json_util._json_convert(resource), 200
        return {"message": "resource not found"}, 404

    # Should probably not be used, since resources shouldn't be removed
    def delete(self, _id):
        try:
            resource = mongo.db.resources.find_one({"_id": ObjectId(_id)})
        except:
            return {"message": "An error occurred trying to look up this resource"}, 500

        if resource:
            try:
                mongo.db.resources.delete_one({"_id": ObjectId(_id)})
            except:
                return {"message": "An error occurred trying to delete this resource"}, 500
            return {"message": "resource was deleted"}, 200
        return {"message": "resource not found"}, 404


class ResourceList(Resource):
    def get(self):
        try:
            resource = mongo.db.resources.find()
        except:
            return {"message": "An error occurred looking up all of the resource"}, 500

        if resource.count():
            return {"resource": json_util._json_convert(resource)}, 200
        return {"message": "No resource(s) were found"}, 404
