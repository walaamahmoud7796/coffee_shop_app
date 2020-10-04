import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


"""
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
"""
# db_drop_and_create_all()

# ROUTES


@app.route("/drinks", methods=["GET"])
def get_drinks():

    drinks = Drink.query.all()
    if len(drinks) > 0:
        drinks = [drink.short() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": drinks
        })
    else:
        abort(404)


@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def get_drinks_detail(jwt):
    drinks = Drink.query.all()
    if len(drinks) > 0:
        drinks = [drink.long() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": drinks
        })
    else:
        abort(404)


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def post_drinks(payload):

    data = json.loads(request.data)
    try:
        drink = Drink(title=data['title'], recipe=json.dumps(data["recipe"]))
        drink.insert()
        return jsonify({"success": True, "drinks": [drink.long()]})
    except Exception as e:
        abort(422)


@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def patch_drinks(jwt, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink:
        data = json.loads(request.data)
        new_title = data['title']
        new_recipe = data['recipe']
        if new_title:
            drink.title = new_title
        if new_recipe:
            drink.recipe = json.dumps(new_recipe)
        drink.update()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    else:
        abort(404)


@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drinks(jwt, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink:
        drink.delete()
        return jsonify({
            "success": True,
            "delete": id
        })
    else:
        abort(404)


# Error Handling


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False,
                    "error": 400,
                    "message": "Bad Request"}), 400


@app.errorhandler(403)
def forbidden(error):
    return jsonify({"success": False,
                    "error": 403,
                    "message": "forbidden"}), 403


@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False,
                    "error": 404,
                    "message": "resource not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"success": False,
                    "error": 405,
                    "message": "Method Not Allowed"}), 405


@app.errorhandler(409)
def duplicate_resource(error):
    return jsonify({"success": False,
                    "error": 409,
                    "message": "duplicate_resource"}), 409


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({"success": False,
                    "error": 422,
                    "message": "unprocessable"}), 422


@app.errorhandler(500)
def server_error(error):
    return jsonify({"success": False,
                    "error": 500,
                    "message": "Server Error"}), 500


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
