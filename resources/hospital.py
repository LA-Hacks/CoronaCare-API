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

_hospital_parser = reqparse.RequestParser()
_hospital_parser.add_argument(
    "name", type=str, required=True, help="This field cannot be blank."
)
_hospital_parser.add_argument(
    "address", type=str, required=True, help="This field cannot be blank."
)
_hospital_parser.add_argument(
    "city_state", type=str, required=True, help="This field cannot be blank."
)
_hospital_parser.add_argument(
    "zip", type=str, required=True, help="This field cannot be blank."
)


class HospitalRegister(Resource):
    def post(self):
        data = _hospital_parser.parse_args()

        try:
            hospital = mongo.db.hospitals.find_one(
                {"name": data["name"]})
        except:
            return {"message": "An error occurred looking up the hospital"}, 500

        if hospital:
            return {"message": "A hospital with that username already exists"}, 400

        try:
            mongo.db.hospitals.insert_one({
                "name": data["name"],
                "address": data["address"],
                "city_state": data["city_state"],
                "zip": data["zip"]
            })

            return {"message": "Hospital created successfully."}, 201
        except:
            return {"message": "An error occurred creating the hospital"}, 500


class Hospital(Resource):
    def get(self, _id):
        try:
            hospital = mongo.db.hospitals.find_one({"_id": ObjectId(_id)})
        except:
            return {"message": "An error occurred looking up the hospital"}, 500

        if hospital:
            return json_util._json_convert(hospital), 200
        return {"message": "hospital not found"}, 404

    # Should probably not be used, since user depends on this staying forever
    def delete(self, _id):
        try:
            hospital = mongo.db.hospitals.find_one({"_id": ObjectId(_id)})
        except:
            return {"message": "An error occurred trying to look up this hospital"}, 500

        if hospital:
            try:
                mongo.db.hospitals.delete_one({"_id": ObjectId(_id)})
            except:
                return {"message": "An error occurred trying to delete this hospital"}, 500
            return {"message": "hospital was deleted"}, 200
        return {"message": "hospital not found"}, 404


class HospitalList(Resource):
    def get(self):
        try:
            hospitals = mongo.db.hospitals.find()
        except:
            return {"message": "An error occurred looking up all of the hospitals"}, 500

        if hospitals.count():
            return {"hospitals": json_util._json_convert(hospitals)}, 200
        return {"message": "No hospitals were found"}, 404
