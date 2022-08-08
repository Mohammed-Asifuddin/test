"""
Customer API service
"""
# import os
from flask_api import status
from flask import jsonify, request
from src import app
from src.helpers import file_validator as fv
from src.helpers.gCloud import storage_handler as sh
from src.helpers.gCloud import firestore_helper as fh

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
    if len(bucket_name) < 3:
        bucket_name = bucket_name + "000"
    doc_id_list = fh.get_customer_by_bucket_name(bucket_name)
    if len(doc_id_list) != 0:
        resp = jsonify({"message": "Customer Exists"})
        resp.status_code = 400
        return resp
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
    customer_dict = {}
    customer_dict["name"] = name
    customer_dict["bucket_name"] = bucket_name
    customer_dict["logo_file_path"] = logo_public_url
    customer_dict["intent_file_path"] = intent_public_url
    customer_dict["status"] = False
    customer_dict["training_status"] = 0
    doc = fh.add_customer(customer_dict=customer_dict)
    customer_dict["customer_id"] = doc[-1].id
    # TODO
    # Create a dialog flow agent with customer name : pubsub
    # if we have intent_file we have to trigger pubsub topic to create a intent,
    # we will share customer document id
    resp = jsonify({"message": "Customer created successfully", "data": customer_dict})
    return resp, status.HTTP_201_CREATED


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
    docs = fh.get_customer_by_id(customer_id)
    if not docs.exists:
        resp = jsonify({"message": "No data found with given customer_id"})
        resp.status_code = 400
        return resp
    doc = docs.to_dict()
    bucket_name = doc["bucket_name"]
    doc["customer_id"] = customer_id
    bucket = sh.get_bucket_object_by_name(bucket_name)
    logo_file = ""
    logo_public_url = ""
    if "logo_file" in request.files:
        logo_file = request.files["logo_file"]
        if logo_file.filename == "":
            resp = jsonify({"message": "No Logo file part in the request"})
            resp.status_code = 400
            return resp
        if logo_file and not fv.allowed_image_file(logo_file.filename):
            resp = jsonify({"message": "Allowed Logo file types are csv"})
            resp.status_code = 400
            return resp
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
    doc_updated = False
    if logo_public_url != "":
        doc["logo_file_path"] = logo_public_url
        doc_updated = True
    if intent_public_url != "":
        doc["intent_file_path"] = intent_public_url
        doc_updated = True
    if doc_updated:
        fh.update_customer_by_id(doc_id=customer_id, doc_dict=doc)
    # TODO
    # Create a dialog flow agent with customer name : pubsub
    # if we have intent_file we have to trigger pubsub topic to create a intent,
    # we will share customer document id
    resp = jsonify({"message": "Customer updated", "data": doc})
    return resp, status.HTTP_201_CREATED


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
