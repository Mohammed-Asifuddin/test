"""
Customer API service
"""
# import os
# from flask_api import status
import string
from flask import jsonify, request
from src import app
from src.helpers import file_validator as fv
from src.helpers.gCloud import storage_handler as sh

ROUTE = "/customer"

@app.route(ROUTE, methods=["POST"])
def create_customer():
    """
    Create a new customer
    """
    name = request.form["name"]
    if name.strip() == "":
        resp = jsonify({"message": "Name is neither empty nor blank"})
        resp.status_code = 400
        return resp
    if "logo_file" not in request.files:
        resp = jsonify({"message": "Logo is mandatory."})
        resp.status_code = 400
        return resp
    logo_file = request.files["logo_file"]
    if logo_file.filename == "":
        resp = jsonify({"message": "No Logo file part in the request"})
        resp.status_code = 400
        return resp
    if logo_file and not fv.allowed_image_file(logo_file.filename):
        resp = jsonify({"message": "Allowed Logo file types are png, jpg, jpeg, gif"})
        resp.status_code = 400
        return resp
    bucket_name = "".join(char for char in name if char.isalnum()).lower()
    bucket = sh.create_bucket(bucket_name)
    logo_public_url = sh.upload_logo(bucket=bucket, logo_file=logo_file)
    intent_file = ""
    intent_public_url = ""
    if "intent_file" in request.files:
        intent_file = request.files["intent_file"]
        if intent_file.filename == "":
            resp = jsonify({"message": "No Intent file part in the request"})
            resp.status_code = 400
            return resp
        if intent_file and not fv.allowed_intent_file(intent_file.filename):
            resp = jsonify({"message": "Allowed Intent file types are csv"})
            resp.status_code = 400
            return resp
        intent_public_url = sh.upload_intent(bucket=bucket, intent_file=intent_file)
    print(logo_public_url)
    print(intent_public_url)
    resp = jsonify({"message": "File successfully uploaded"})
    resp.status_code = 201
    return resp


@app.route(ROUTE, methods=["PUT"])
def update_customer():
    """
    update a customer
    """
    customer_id = request.form["customer_id"]
    if customer_id.strip() == "":
        resp = jsonify({"message": "customer_id is neither empty nor blank"})
        resp.status_code = 400
        return resp
    # logo_file = request.files["logo_file"]
    # intent_file = request.files["intent_file"]
    # need work on logo and intent file validation
    resp = jsonify({"message": "File successfully uploaded"})
    resp.status_code = 201
    return resp


@app.route(ROUTE, methods=["GET"])
def get_all_customer():
    """
    Get all customers data
    """
    list_data = []
    all_customer_dict = {
        "customerId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "customerName": "string",
        "customerLogoPath": "string",
        "customerStatus": True,
        "customerTrainingStatus": 0,
    }
    all_customer_dict2 = {
        "customerId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "customerName": "string",
        "customerLogoPath": "string",
        "customerStatus": True,
        "customerTrainingStatus": 0,
    }
    list_data.append(all_customer_dict)
    list_data.append(all_customer_dict2)
    resp = jsonify(list_data)
    resp.status_code = 200
    return resp


@app.route(ROUTE + "/<customer_id>", methods=["GET"])
def delete_customer(customer_id):
    """
    Delete customers data
    """
    customer_id = request.view_args["customer_id"]
    print(customer_id)
    resp = jsonify({"message": "Customer deleted successfully"})
    resp.status_code = 200
    return resp


@app.route(ROUTE + "/<customer_id>/<customer_status>", methods=["PUT"])
def update_customer_status(customer_id, customer_status):
    """
    Delete customers data
    """
    customer_id = request.view_args["customer_id"]
    customer_status = request.view_args["customer_status"]
    print(customer_id)
    print(customer_status)
    resp = jsonify({"message": "Customer status changed successfully"})
    resp.status_code = 200
    return resp
