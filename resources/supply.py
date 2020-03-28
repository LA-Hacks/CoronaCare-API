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


_supply_parser = reqparse.RequestParser()
_supply_parser.add_argument(
    "resource_name", type=str, required=True, help="This field cannot be blank."
)
_supply_parser.add_argument(
    "resource_id", type=str, required=True, help="This field cannot be blank."
)
_supply_parser.add_argument(
    "quantity", type=int, required=True, help="This field cannot be blank."
)


class ResourceSupplyRegister(Resource):
    @jwt_required
    def post(self):
        data = _supply_parser.parse_args()

        try:
            user = mongo.db.users.find_one(
                {"_id": ObjectId(get_jwt_identity())})
        except:
            return {"message": "There was an error looking up the user"}, 500

        try:
            provider = mongo.db.providers.find_one(
                {"_id": ObjectId(user['provider_id'])})
        except:
            return {"message": "There was an error looking up the provider"}, 500

        # check to see if there is a pending supply for that resource
        try:
            supply = mongo.db.supplies.find_one(
                {"resource_id": data['resource_id'], "provider_id": str(provider['_id'])})
        except:
            return {"message": "There was an error looking up the resource"}, 500

        if supply:
            try:
                mongo.db.supplies.update_one(
                    {"_id": supply.get("_id")},
                    {"$set": {"quantity": supply.get(
                        "quantity", 0) + data.get("quantity", 0)}},
                )
            except:
                return {"message": "there was an error updating the resource supply"}, 500
            return {"message": "resource supply updated"}, 200

        # if there is no pending supply for that resource, create one
        try:
            mongo.db.supplies.insert_one({
                "resource_id": data['resource_id'],
                "provider_id": str(provider['_id']),
                "quantity": data['quantity']
            })
        except:
            return {"message": "There was an error creating the resource supply"}, 500

        return {"message": "resource supply created"}, 201


class ResourceSupply(Resource):
    @jwt_required
    def get(self, _id):
        try:
            supply = mongo.db.supplies.find_one({"_id": ObjectId(_id)})
        except:
            return {"message": "An error occurred looking up the supply"}, 500

        if supply:
            return json_util._json_convert(supply), 200
        return {"message": "supply not found"}, 404

    # Should probably not be used, since user depends on this staying forever
    @jwt_required
    def delete(self, _id):
        try:
            supply = mongo.db.supplies.find_one({"_id": ObjectId(_id)})
        except:
            return {"message": "An error occurred trying to look up this supply"}, 500

        if supply:
            try:
                mongo.db.supplies.delete_one({"_id": ObjectId(_id)})
            except:
                return {"message": "An error occurred trying to delete this supply"}, 500
            return {"message": "supply was deleted"}, 200
        return {"message": "supply not found"}, 404


class ResourceSupplyList(Resource):
    @jwt_required
    def get(self):
        try:
            user = mongo.db.users.find_one(
                {"_id": ObjectId(get_jwt_identity())})
        except:
            return {"message": "There was an error looking up the user"}, 500

        try:
            provider = mongo.db.providers.find_one(
                {"_id": ObjectId(user['provider_id'])})
        except:
            return {"message": "There was an error looking up the provider"}, 500

        try:
            supplies = mongo.db.supplies.find({
                "provider_id": str(provider['_id'])
            })
        except:
            return {"message": "There was an error looking up the resource supply"}, 500

        return {"supplies": json_util._json_convert(supplies)}, 200
