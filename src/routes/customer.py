"""
Customer API service
"""
import os
import time
from flask_cors import cross_origin
from flask_api import status
from flask import jsonify, request
from src import app
from src.helpers import file_validator as fv
from src.helpers.gCloud import storage_handler as sh
from src.helpers.gCloud import firestore_helper as fh
from src.helpers.gCloud import dialogflow as df
from src.helpers import constant
from src.routes import intents

ROUTE = "/customer"


def validate_files_as_mandatory(files, file_type):
    """
    File validator as mandatory
    """
    if file_type not in files:
        resp = jsonify({constant.MESSAGE: file_type + " is mandatory."})
        resp.status_code = 400
        return resp
    file = files[file_type]
    if file.filename == "":
        resp = jsonify({constant.MESSAGE: "No " + file_type + " part in the request"})
        resp.status_code = 400
        return resp
    if (not fv.allowed_image_file(file.filename)) and (
        file_type == constant.LOGO_FILE_PATH
    ):
        resp = jsonify({constant.MESSAGE: constant.ALLOWED_IMAGES_MESSAGE})
        resp.status_code = 400
        return resp
    if (not fv.allowed_video_file(file.filename)) and (
        file_type == constant.VIDEO_FILE_PATH
    ):
        resp = jsonify(
            {constant.MESSAGE: "Allowed Video file types are mp4, mov, mp4v, avi"}
        )
        resp.status_code = 400
        return resp
    return ""


def validate_files_as_optional(files, file_type):
    """
    File validator as optional
    """
    if (file_type in files) and (files[file_type]):
        file = files[file_type]
        if (
            not fv.allowed_image_file(file.filename)
            and file_type == constant.LOGO_FILE_PATH
        ):
            resp = jsonify({constant.MESSAGE: constant.ALLOWED_IMAGES_MESSAGE})
            resp.status_code = 400
            return resp
        if (
            not fv.allowed_intent_file(file.filename)
            and file_type == constant.INTENT_FILE_PATH
        ):
            resp = jsonify({constant.MESSAGE: "Allowed intent file types are CSV"})
            resp.status_code = 400
            return resp
        if (
            not fv.allowed_video_file(file.filename)
            and file_type == constant.VIDEO_FILE_PATH
        ):
            resp = jsonify(
                {constant.MESSAGE: "Allowed video file types are mp4, mov, mp4v, avi"}
            )
            resp.status_code = 400
            return resp
    return ""


def is_duplicate_customer(bucket_name):
    """
    Validate is customer is duplicate.
    """
    if len(bucket_name) < 3:
        bucket_name = bucket_name + "000"
    doc_id_list = fh.get_customer_by_bucket_name(bucket_name)
    if len(doc_id_list) == 0:
        return len(doc_id_list)
    resp = jsonify({constant.MESSAGE: "Customer Exists"})
    resp.status_code = 400
    return resp


def customer_id_validation(customer_id):
    """
    Update status common code
    """
    if customer_id.strip() == "":
        resp = jsonify({constant.MESSAGE: "customer_id is neither empty nor blank"})
        resp.status_code = 400
        return resp
    docs = fh.get_customer_by_id(customer_id)
    if not docs.exists:
        resp = jsonify({constant.MESSAGE: "No data found with given customer_id"})
        resp.status_code = 400
        return resp
    doc = docs.to_dict()
    if doc["is_deleted"]:
        resp = jsonify({constant.MESSAGE: "Customer already deleted."})
        resp.status_code = 400
        return resp
    return doc


@app.route(ROUTE, methods=["POST"])
@cross_origin()
def create_customer():
    """
    Create a new customer
    """
    if "name" not in request.form.keys():
        resp = jsonify({constant.MESSAGE: "Name is mandatory fields"})
        resp.status_code = 400
        return resp
    name = request.form["name"]
    if name.strip() == "":
        resp = jsonify({constant.MESSAGE: "Name is neither empty nor blank"})
        resp.status_code = 400
        return resp
    bucket_name = "".join(char for char in name if char.isalnum()).lower()
    customer_duplicate = is_duplicate_customer(bucket_name=bucket_name)
    files = request.files
    logo_resp = validate_files_as_mandatory(
        files=files, file_type=constant.LOGO_FILE_PATH
    )
    intent_resp = validate_files_as_optional(
        files=files, file_type=constant.INTENT_FILE_PATH
    )
    if logo_resp != "":
        return logo_resp
    if intent_resp != "":
        return intent_resp
    bucket = ""
    customer_dict = {}
    customer_dict["name"] = name
    customer_dict["bucket_name"] = bucket_name
    customer_dict["status"] = False
    customer_dict["training_status"] = 0
    customer_dict["is_deleted"] = False
    customer_dict["customer_display_id"] = str(int(time.time())).split(".", maxsplit=1)[
        0
    ]
    if customer_duplicate == 0:
        bucket = sh.create_bucket(bucket_name)
        logo_file = files[constant.LOGO_FILE_PATH]
        logo_public_url = sh.upload_logo(bucket=bucket, logo_file=logo_file)
        customer_dict[constant.LOGO_FILE_PATH] = logo_public_url
        if (
            (constant.INTENT_FILE_PATH in files)
            and files[constant.INTENT_FILE_PATH]
            and (files[constant.INTENT_FILE_PATH].filename != "")
        ):
            intent_file = files[constant.INTENT_FILE_PATH]
            intent_public_url = sh.upload_intent(bucket=bucket, intent_file=intent_file)
            customer_dict[constant.INTENT_FILE_PATH] = intent_public_url
    else:
        return customer_duplicate
    doc = fh.add_customer(customer_dict=customer_dict)
    customer_dict[constant.CUSTOMER_ID] = doc[-1].id
    agent_response = df.create_agent(os.getenv("PROJECT_ID", "retail-btl-dev"), name)
    agent_dict = {}
    agent_dict[constant.CUSTOMER_ID]=doc[-1].id
    agent_dict['agent_id'] = (agent_response.name.split('/'))[-1]
    agent_dict['display_name'] = doc['name']
    fh.add_agent(agent_dict=agent_dict)
    # TODO : send pubsub notification to create Intent
    resp = jsonify(
        {constant.MESSAGE: "Customer created successfully", "data": customer_dict}
    )
    return resp, status.HTTP_201_CREATED


@app.route(ROUTE, methods=["PUT"])
@cross_origin()
def update_customer():
    """
    update a customer
    """
    if constant.CUSTOMER_ID not in request.form.keys():
        resp = jsonify({constant.MESSAGE: "customer_id is mandatory"})
        resp.status_code = 400
        return resp
    customer_id = request.form[constant.CUSTOMER_ID]
    doc = customer_id_validation(customer_id=customer_id)
    if not isinstance(doc, (dict)):
        return doc
    files = request.files
    bucket = sh.get_bucket_object_by_name(doc["bucket_name"])
    logo_resp = validate_files_as_optional(
        files=files, file_type=constant.LOGO_FILE_PATH
    )
    is_updated = False
    if (
        logo_resp == ""
        and constant.LOGO_FILE_PATH in files
        and files[constant.LOGO_FILE_PATH].filename != ""
    ):
        logo_file = files[constant.LOGO_FILE_PATH]
        if logo_file:
            logo_public_url = sh.upload_logo(bucket=bucket, logo_file=logo_file)
            doc[constant.LOGO_FILE_PATH] = logo_public_url
            is_updated = True
    else:
        return logo_resp
    intent_resp = validate_files_as_optional(
        files=files, file_type=constant.INTENT_FILE_PATH
    )
    if (
        intent_resp == ""
        and constant.INTENT_FILE_PATH in files
        and files[constant.INTENT_FILE_PATH].filename != ""
    ):
        intent_file = files[constant.INTENT_FILE_PATH]
        if intent_file:
            intent_public_url = sh.upload_intent(bucket=bucket, intent_file=intent_file)
            doc[constant.INTENT_FILE_PATH] = intent_public_url
            is_updated = True
    else:
        return intent_resp
    if is_updated:
        fh.update_customer_by_id(doc_id=customer_id, doc_dict=doc)
    # TODO : send pubsub notification to create Intent
    resp = jsonify({constant.MESSAGE: "Customer updated", "data": doc})
    return resp, status.HTTP_200_OK


@app.route(ROUTE, methods=["GET"])
def get_all_customer():
    """
    Get all customers data
    """
    list_data = []
    docs = fh.get_all_customers()
    for doc in docs:
        data = doc.to_dict()
        data[constant.CUSTOMER_ID] = doc.id
        list_data.append(data)
    resp = jsonify(list_data)
    return resp, status.HTTP_200_OK


@app.route(ROUTE + "/active", methods=["GET"])
def get_active_customer():
    """
    Get active customers data
    """
    list_data = []
    docs = fh.get_active_customer()
    for doc in docs:
        data = doc.to_dict()
        data[constant.CUSTOMER_ID] = doc.id
        list_data.append(data)
    if len(list_data) != 0:
        resp = jsonify(list_data[0])
    else:
        resp = {}
    return resp, status.HTTP_200_OK


@app.route(ROUTE + "/<customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    """
    Delete customers data
    """
    doc = customer_id_validation(customer_id=customer_id)
    if not isinstance(doc, (dict)):
        return doc
    doc["is_deleted"] = True
    fh.update_customer_by_id(doc_id=customer_id, doc_dict=doc)
    resp = jsonify({constant.MESSAGE: "Customer deleted successfully"})
    resp.status_code = 200
    return resp


@app.route(ROUTE + "/status", methods=["PUT"])
def update_customer_status():
    """
    Update customers status
    """
    current_customer_id: any
    current_customer_doc: any
    new_customer_id: any
    new_customer_doc: any
    if (
        "current_customer_id" in request.form.keys()
        and request.form["current_customer_id"] != ""
    ):
        current_customer_id = request.form["current_customer_id"]
        current_customer_doc = customer_id_validation(customer_id=current_customer_id)
        if not isinstance(current_customer_doc, (dict)):
            return current_customer_doc
        current_customer_doc["status"] = False
    else:
        current_customer_doc = {}
    if (
        "new_customer_id" in request.form.keys()
        and request.form["new_customer_id"] != ""
    ):
        new_customer_id = request.form["new_customer_id"]
        new_customer_doc = customer_id_validation(customer_id=new_customer_id)
        if not isinstance(new_customer_doc, (dict)):
            return new_customer_doc
        new_customer_doc["status"] = True
    else:
        new_customer_doc = {}
    if len(current_customer_doc.keys()) != 0:
        fh.update_customer_by_id(
            doc_id=current_customer_id, doc_dict=current_customer_doc
        )
    if len(new_customer_doc.keys()) != 0:
        fh.update_customer_by_id(doc_id=new_customer_id, doc_dict=new_customer_doc)
    resp = jsonify({constant.MESSAGE: "Customer status changed successfully"})
    resp.status_code = 200
    return resp

@app.route(ROUTE + "/<customer_id>/intent", methods=["POST"])
def manageIntentsForCustomer(customer_id):
    """
    Add/Update/Delete customer intents
    """
    print("In manageIntentsForCustomer()")
    return intents.addUpdateDeleteIntents(customer_id, "")

@app.route(ROUTE + "/<customer_id>/intent", methods=["GET"])
def getIntentsForCustomer(customer_id):
    return intents.getIntents(customer_id, "")