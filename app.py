import os

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from blacklist import BLACKLIST

# create the app instance
app = Flask(__name__)


app.config["MONGO_URI"] = (
    os.environ.get("MONGODB_URI", "mongodb://localhost:27017/CoronaCare")
    + "?retryWrites=false"
)
app.config[
    "PROPAGATE_EXCEPTIONS"
] = True  # exceptions are re-raised rather than being handled by app's error handlers
app.config["JWT_BLACKLIST_ENABLED"] = True  # enable blacklist feature
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = [
    "access",
    "refresh",
]  # allow blacklisting for access and refresh tokens
app.config["JWT_SECRET_KEY"] = "secret"  #

# creates an instance of flask-restful api that will be used to add our resources
api = Api(app)

# creates an instance of jwt manager that will handle authentication for the application
jwt = JWTManager(app)


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    # Here we blacklist particular JWTs that have been created in the past.
    return decrypted_token["jti"] in BLACKLIST


# The following callbacks are used for customizing jwt response/error messages for certain situations.
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        jsonify(
            {"message": "Signature verification failed.", "error": "invalid_token"}
        ),
        401,
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required",
            }
        ),
        401,
    )


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return (
        jsonify(
            {"description": "The token is not fresh.",
                "error": "fresh_token_required"}
        ),
        401,
    )


@jwt.revoked_token_loader
def revoked_token_callback():
    return (
        jsonify(
            {"description": "The token has been revoked.", "error": "token_revoked"}
        ),
        401,
    )


if __name__ == "__main__":
    from db import mongo

    mongo.init_app(app)
    app.run(port=5000, debug=True)
