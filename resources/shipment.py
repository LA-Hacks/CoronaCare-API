import traceback

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

_shipment_parser = reqparse.RequestParser()
_shipment_parser.add_argument(
    "resource_name", type=str, required=True, help="This field cannot be blank."
)
_shipment_parser.add_argument(
    "resource_id", type=str, required=True, help="This field cannot be blank."
)
_shipment_parser.add_argument(
    "quantity", type=int, required=True, help="This field cannot be blank."
)
_shipment_parser.add_argument(
    "standard", type=int, required=True, help="This field cannot be blank."
)
_shipment_parser.add_argument(
    "hospital_id", type=int, required=True, help="This field cannot be blank."
)
_shipment_parser.add_argument(
    "provider_id", type=int, required=True, help="This field cannot be blank."
)

_shipment_update_parser = reqparse.RequestParser()
_shipment_parser.add_argument(
    "shipped", type=bool, required=False, help="This field cannot be blank."
)
_shipment_parser.add_argument(
    "received", type=bool, required=False, help="This field cannot be blank."
)


class ShipmentCreator:
    @classmethod
    def fromRequestCreate(cls, data):
        # search for a supply
        try:
            supplies = mongo.db.supplies.find(
                {"resource_id": data['resource_id'], "standard": data['standard']})
        except:
            print("There was an error looking up supplies")
            return

        # iterate over all of them and pick the one that matches or one that has the most quantity
        shipment_count = 0
        provider_id = None
        for supply in supplies:
            if data.get("quantity", 0) == supply.get("quantity", 0):
                shipment_count = supply.get("quantity")
                provider_id = str(supply.get("provider_id"))
                break
            elif supply.get("quantity", 0) > shipment_count:
                shipment_count = supply.get("quantity")
                provider_id = str(supply.get("_id"))

        # send the request id and the shipment id to the ShipmentRegister
        if provider_id:
            cls.createShipment({
                "resource_name": data.get("name"),
                "resource_id": data.get("resource_id"),
                "quantity": shipment_count,
                "standard": data.get("standard"),
                "hospital_id": data.get("hospital_id"),
                "provider_id": provider_id
            })

    @classmethod
    def fromSupplyCreate(cls, data):
        # search for a request
        try:
            requests = mongo.db.requests.find(
                {"resource_id": data['resource_id'], "standard": data['standard']})
        except:
            print("There was an error looking up supplies")
            return

        # iterate over all of them and pick the one that matches or one that has the most quantity
        for request in requests:
            if data.get("quantity", 0) <= 0:
                break

            shipment_count = min(data.get("quantity", 0),
                                 request.get("quantity", 0))

            print(cls.createShipment({
                "resource_name": data.get("resource_name"),
                "resource_id": data.get("resource_id"),
                "quantity": shipment_count,
                "standard": data["standard"],
                "hospital_id": request.get("hospital_id"),
                "provider_id": data.get("provider_id")
            }))

            data['quantity'] = data.get("quantity", 0) - shipment_count

    @classmethod
    def createShipment(cls, data):
         # lookup the provider order and decrement by quantity, if zero, delete it
        try:
            supply = mongo.db.supplies.find_one(
                {"resource_id": data['resource_id'], "standard": data['standard'], "provider_id": data['provider_id']})
        except:
            return {"message": "There was an error looking up the resource"}, 500

        if supply.get("quantity", 0) - data.get("quantity", 0) > 0:
            try:
                mongo.db.supplies.update_one(
                    {"_id": supply.get("_id")},
                    {"$set": {"quantity": supply.get(
                        "quantity", 0) - data.get("quantity", 0)}},
                )
            except:
                return {"message": "there was an error updating the resource supply"}, 500
        else:
            try:
                mongo.db.supplies.delete_one({"_id": supply.get("_id")})
            except:
                return {"message": "An error occurred trying to delete this supply"}, 500

        # lookup the hospital order and decrement by quantity, if zero, delete it
        try:
            request = mongo.db.requests.find_one(
                {"resource_id": data['resource_id'], "hospital_id": data['hospital_id']})
        except:
            return {"message": "There was an error looking up the resource request"}, 500

        if request.get("quantity", 0) - data.get("quantity", 0) > 0:
            try:
                mongo.db.requests.update_one(
                    {"_id": request.get("_id")},
                    {"$set": {"quantity": request.get(
                        "quantity", 0) - data.get("quantity", 0)}},
                )
            except:
                return {"message": "there was an error updating the resource request"}, 500
        else:
            try:
                mongo.db.requests.delete_one({"_id": request.get("_id")})
            except:
                return {"message": "An error occurred trying to delete this request"}, 500

        try:
            hospital = mongo.db.hospitals.find_one(
                {"_id": ObjectId(data['hospital_id'])})
            provider = mongo.db.providers.find_one(
                {"_id": ObjectId(data['provider_id'])})
        except:
            return {"message": "An error ocurred tyring to lookup the hospital and the provider"}, 500

        # create the shipment
        try:
            # should also have the to address, from address, and resource name
            mongo.db.shipments.insert_one({
                "resource_name": data['resource_name'],
                "resource_id": data['resource_id'],
                "quantity": data['quantity'],
                "standard": data['standard'],
                "provider_id": data['provider_id'],
                "hospital_id": data['hospital_id'],
                "hospital": hospital,
                "provider": provider
            })
        except:
            traceback.print_exc()
            return {"message": "There was an error creating the shipment"}, 500

        return {"message": "shipment created"}, 201


class ShipmentRegister(Resource):

    # TODO: add twilio
    @jwt_required
    def post(self):
        data = _shipment_parser.parse_args()

        # lookup the provider order and decrement by quantity, if zero, delete it
        try:
            supply = mongo.db.supplies.find_one(
                {"resource_id": data['resource_id'], "standard": data['standard'], "provider_id": data['provider_id']})
        except:
            return {"message": "There was an error looking up the resource"}, 500

        if supply.get("quantity", 0) - data.get("quantity", 0) > 0:
            try:
                mongo.db.supplies.update_one(
                    {"_id": supply.get("_id")},
                    {"$set": {"quantity": supply.get(
                        "quantity", 0) - data.get("quantity", 0)}},
                )
            except:
                return {"message": "there was an error updating the resource supply"}, 500
        else:
            try:
                mongo.db.supplies.delete_one({"_id": supply.get("_id")})
            except:
                return {"message": "An error occurred trying to delete this supply"}, 500

        # lookup the hospital order and decrement by quantity, if zero, delete it
        try:
            request = mongo.db.requests.find_one(
                {"resource_id": data['resource_id'], "standard": data['standard'], "hospital_id": data['hospital_id']})
        except:
            return {"message": "There was an error looking up the resource request"}, 500

        if request.get("quantity", 0) - data.get("quantity", 0) > 0:
            try:
                mongo.db.requests.update_one(
                    {"_id": request.get("_id")},
                    {"$set": {"quantity": request.get(
                        "quantity", 0) - data.get("quantity", 0)}},
                )
            except:
                return {"message": "there was an error updating the resource request"}, 500
        else:
            try:
                mongo.db.requests.delete_one({"_id": request.get("_id")})
            except:
                return {"message": "An error occurred trying to delete this request"}, 500

        try:
            hospital = mongo.db.hospitals.find_one(
                {"_id": ObjectId(data['hospital_id'])})
            provider = mongo.db.providers.find_one(
                {"_id": ObjectId(data['provider_id'])})
        except:
            return {"message": "An error ocurred tyring to lookup the hospital and the provider"}, 500

        # create the shipment
        try:
            mongo.db.shipments.insert_one({
                "resource_name": data["resource_name"],
                "resource_id": data['resource_id'],
                "quantity": data['quantity'],
                "standard": data['standard'],
                "provider_id": data['provider_id'],
                "hospital_id": data['hospital_id'],
                "hospital": hospital,
                "provider": provider,
            })
        except:
            return {"message": "There was an error creating the shipment"}, 500

        return {"message": "shipment created"}, 201


class Shipment(Resource):

    @jwt_required
    def get(self, _id):
        try:
            shipment = mongo.db.shipments.find_one({"_id": ObjectId(_id)})
        except:
            return {"message": "An error occurred looking up the shipment"}, 500

        if shipment:
            return json_util._json_convert(shipment), 200
        return {"message": "shipment not found"}, 404

    @jwt_required
    def put(self, _id):
        data = _shipment_update_parser.parse_args()

        try:
            shipment = mongo.db.shipments.find_one(
                {"_id": shipment.get("_id")})
        except:
            return {"message": "There was an error looking up the shipment"}, 500

        if shipment:
            try:
                mongo.db.shipments.update_one(
                    {"_id": shipment.get("_id")},
                    {"$set": {
                        "shipped": shipment.get("shipped", False) or data.get("shipped", False),
                        "arrived": shipment.get("arrived", False) or data.get("arrived", False)
                    }})
            except:
                return {"message": "there was an error updating the shipment"}, 500
            return {"message": " shipment updated"}, 200

        return {"message": "this shipment does not exist"}, 404

    # Should probably not be used, since user depends on this staying forever
    @jwt_required
    def delete(self, _id):
        try:
            shipment = mongo.db.shipments.find_one({"_id": ObjectId(_id)})
        except:
            return {"message": "An error occurred trying to look up this shipment"}, 500

        if shipment:
            try:
                mongo.db.shipments.delete_one({"_id": ObjectId(_id)})
            except:
                return {"message": "An error occurred trying to delete this shipment"}, 500
            return {"message": "shipment was deleted"}, 200
        return {"message": "shipment not found"}, 404


class ShipmentList(Resource):
    @jwt_required
    def get(self):
        try:
            user = mongo.db.users.find_one(
                {"_id": ObjectId(get_jwt_identity())})
        except:
            return {"message": "There was an error looking up the user"}, 500

        if user.get('provider_id'):
            try:
                provider = mongo.db.providers.find_one(
                    {"_id": ObjectId(user['provider_id'])})
            except:
                return {"message": "There was an error looking up the provider"}, 500

            try:
                shipments = mongo.db.shipments.find({
                    "provider_id": str(provider['_id'])
                })
            except:
                return {"message": "There was an error looking up the resource supply"}, 500
        else:
            try:
                hospital = mongo.db.hospitals.find_one(
                    {"_id": ObjectId(user['hospital_id'])})
            except:
                return {"message": "There was an error looking up the hospital"}, 500

            try:
                shipments = mongo.db.shipments.find({
                    "hospital_id": str(hospital['_id'])
                })
            except:
                return {"message": "There was an error looking up the resource request"}, 500

        return {"shipments": json_util._json_convert(shipments)}, 200
