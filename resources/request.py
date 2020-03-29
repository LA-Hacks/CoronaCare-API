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
from resources.shipment import ShipmentCreator

_request_parser = reqparse.RequestParser()
_request_parser.add_argument(
    "resource_name", type=str, required=True, help="This field cannot be blank."
)
_request_parser.add_argument(
    "resource_id", type=str, required=True, help="This field cannot be blank."
)
_request_parser.add_argument(
    "standard", type=str, required=True, help="This field cannot be blank."
)
_request_parser.add_argument(
    "quantity", type=int, required=True, help="This field cannot be blank."
)


class ResourceRequestRegister(Resource):
    @jwt_required
    def post(self):
        data = _request_parser.parse_args()

        try:
            user = mongo.db.users.find_one(
                {"_id": ObjectId(get_jwt_identity())})
        except:
            return {"message": "There was an error looking up the user"}, 500

        try:
            hospital = mongo.db.hospitals.find_one(
                {"_id": ObjectId(user['hospital_id'])})
        except:
            return {"message": "There was an error looking up the hospital"}, 500

        # check to see if there is a pending request for that resource
        try:
            request = mongo.db.requests.find_one(
                {"resource_id": data['resource_id'], "standard": data["standard"], "hospital_id": str(hospital['_id'])})
        except:
            return {"message": "There was an error looking up the resource"}, 500

        if request:
            try:
                mongo.db.requests.update_one(
                    {"_id": request.get("_id")},
                    {"$set": {"quantity": request.get(
                        "quantity", 0) + data.get("quantity", 0)}},
                )
            except:
                return {"message": "there was an error updating the resource request"}, 500
            return {"message": "resource requested updated"}, 200

        # if there is no pending request for that resource, create one
        try:
            mongo.db.requests.insert_one({
                "resource_name": data['resource_name'],
                "resource_id": data['resource_id'],
                "standard": data["standard"],
                "hospital_id": str(hospital['_id']),
                "quantity": data['quantity']
            })
        except:
            return {"message": "There was an error creating the resource request"}, 500

        data['hospital_id'] = str(hospital['_id'])

        ShipmentCreator.fromRequestCreate(data)

        return {"message": "resource request created"}, 201


class ResourceRequest(Resource):
    @jwt_required
    def get(self, _id):
        try:
            request = mongo.db.requests.find_one({"_id": ObjectId(_id)})
        except:
            return {"message": "An error occurred looking up the request"}, 500

        if request:
            return json_util._json_convert(request), 200
        return {"message": "request not found"}, 404

    # Should probably not be used, since user depends on this staying forever
    @jwt_required
    def delete(self, _id):
        try:
            request = mongo.db.requests.find_one({"_id": ObjectId(_id)})
        except:
            return {"message": "An error occurred trying to look up this request"}, 500

        if request:
            try:
                mongo.db.requests.delete_one({"_id": ObjectId(_id)})
            except:
                return {"message": "An error occurred trying to delete this request"}, 500
            return {"message": "request was deleted"}, 200
        return {"message": "request not found"}, 404


class ResourceRequestList(Resource):
    @jwt_required
    def get(self):
        try:
            user = mongo.db.users.find_one(
                {"_id": ObjectId(get_jwt_identity())})
        except:
            return {"message": "There was an error looking up the user"}, 500

        try:
            hospital = mongo.db.hospitals.find_one(
                {"_id": ObjectId(user['hospital_id'])})
        except:
            return {"message": "There was an error looking up the hospital"}, 500

        try:
            requests = mongo.db.requests.find({
                "hospital_id": str(hospital['_id'])
            })
        except:
            return {"message": "There was an error looking up the resource request"}, 500

        return {"requests": json_util._json_convert(requests)}, 200


class ResourceRequestListAll(Resource):
    @jwt_required
    def get(self):
        try:
            requests = mongo.db.requests.find()
        except:
            return {"message": "there was an error looking up the resource requests"}

        return {"requests": json_util._json_convert(requests)}, 200
