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
from src.security.authorize import authorize

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
        resp = jsonify({constant.MESSAGE: constant.ALLOWED_VIDEO_MESSAGE})
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
            resp = jsonify({constant.MESSAGE: constant.ALLOWED_INTENT_MESSAGE})
            resp.status_code = 400
            return resp
        if (
            not fv.allowed_video_file(file.filename)
            and file_type == constant.VIDEO_FILE_PATH
        ):
            resp = jsonify({constant.MESSAGE: constant.ALLOWED_VIDEO_MESSAGE})
            resp.status_code = 400
            return resp
    return ""


def is_duplicate_customer(name):
    """
    Validate is customer is duplicate.
    """
    bucket_name = "".join(char for char in name if char.isalnum()).lower()
    list_customers = []
    docs = fh.get_all_customers()
    for doc in docs:
        data = doc.to_dict()
        customer_name = data[constant.NAME]
        customer_name = "".join(
            char for char in customer_name if char.isalnum()
        ).lower()
        list_customers.append(customer_name)
    if bucket_name not in list_customers:
        return 0
    resp = jsonify({constant.MESSAGE: constant.CUSTOMER_EXISTS_MESSAGE})
    resp.status_code = 400
    return resp


def customer_id_validation(customer_id):
    """
    Update status common code
    """
    if customer_id.strip() == "":
        resp = jsonify({constant.MESSAGE: constant.CUSTOMER_BLANK_MESSAGE})
        resp.status_code = 400
        return resp
    docs = fh.get_customer_by_id(customer_id)
    if not docs.exists:
        resp = jsonify({constant.MESSAGE: constant.CUSTOMER_NO_DATA_MESSAGE})
        resp.status_code = 400
        return resp
    doc = docs.to_dict()
    if doc[constant.IS_DELETED]:
        resp = jsonify({constant.MESSAGE: constant.CUSTOMER_DELETED_MESSAGE})
        resp.status_code = 400
        return resp
    return doc


@app.route(ROUTE, methods=["POST"])
@cross_origin()
@authorize()
def create_customer():
    """
    Create a new customer
    """
    if constant.NAME not in request.form.keys():
        resp = jsonify({constant.MESSAGE: constant.NAME_MANDATORY})
        resp.status_code = 400
        return resp
    name = request.form[constant.NAME]
    if name.strip() == "":
        resp = jsonify({constant.MESSAGE: constant.NAME_NOT_BLANK})
        resp.status_code = 400
        return resp
    customer_duplicate = is_duplicate_customer(name=name)
    bucket_name = "".join(char for char in name if char.isalnum()).lower()
    display_id = str(int(time.time())).split(".", maxsplit=1)[0]
    bucket_name = display_id + "_" + bucket_name
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
    customer_dict[constant.NAME] = name
    customer_dict[constant.BUCKET_NAME] = bucket_name
    customer_dict[constant.STATUS] = False
    customer_dict[constant.TRAINING_STATUS] = 0
    customer_dict[constant.IS_DELETED] = False
    customer_dict[constant.CUSTOMER_DISPLAY_ID] = display_id
    if customer_duplicate == 0:
        bucket = sh.create_bucket(bucket_name)
        logo_file = files[constant.LOGO_FILE_PATH]
        logo_public_url = sh.upload_logo(
            bucket=bucket, logo_file=logo_file, bucket_name=bucket_name
        )
        customer_dict[constant.LOGO_FILE_PATH] = logo_public_url
        if (
            (constant.INTENT_FILE_PATH in files)
            and files[constant.INTENT_FILE_PATH]
            and (files[constant.INTENT_FILE_PATH].filename != "")
        ):
            intent_file = files[constant.INTENT_FILE_PATH]
            customer_dict[constant.INTENT_FILE_PATH] = sh.upload_intent(
                bucket=bucket, intent_file=intent_file, bucket_name=bucket_name
            )
    else:
        return customer_duplicate
    doc = fh.add_customer(customer_dict=customer_dict)
    customer_dict[constant.CUSTOMER_ID] = doc[-1].id
    project_id = os.getenv(constant.PROJECT_ID, constant.DEFAULT_PROJECT_NAME)
    agent_response = df.create_agent(project_id, name)
    agent_dict = {}
    agent_dict[constant.CUSTOMER_ID] = doc[-1].id
    agent_dict[constant.AGENT_ID] = (agent_response.name.split("/"))[-1]
    agent_dict[constant.DISPLAY_NAME] = name
    fh.add_agent(agent_dict=agent_dict)

    #Adding DF changes for initializing new Agent
    anchor_product_page_resp = df.create_default_product_page(project_id, agent_dict[constant.AGENT_ID])
    #Add product_page_resp.name to the customer collection
    customer_dict[constant.ANCHOR_PRODUCT_PAGE] = anchor_product_page_resp.name.split("/")[-1]
    fh.update_customer_by_id(customer_dict[constant.CUSTOMER_ID], customer_dict)

    #Links Start Page to anchor product page
    linked_product_page_resp = df.update_default_flow(project_id, agent_dict[constant.AGENT_ID], customer_dict[constant.ANCHOR_PRODUCT_PAGE])
    print(linked_product_page_resp)

    manage_customer_intents(customer_dict[constant.CUSTOMER_ID])
    resp = jsonify(
        {
            constant.MESSAGE: constant.CUSTOMER_SUCCESS_MESSAGE,
            constant.DATA: customer_dict,
        }
    )
    return resp, status.HTTP_201_CREATED


@app.route(ROUTE, methods=["PUT"])
@cross_origin()
@authorize()
def update_customer():
    """
    update a customer
    """
    print("Customer Update request received")
    if constant.CUSTOMER_ID not in request.form.keys():
        resp = jsonify({constant.MESSAGE: constant.CUSTOMER_MANDATORY})
        resp.status_code = 400
        return resp
    customer_id = request.form[constant.CUSTOMER_ID]
    doc = customer_id_validation(customer_id=customer_id)
    if not isinstance(doc, (dict)):
        return doc
    files = request.files
    bucket = sh.get_bucket_object_by_name(doc[constant.BUCKET_NAME])
    logo_resp = validate_files_as_optional(
        files=files, file_type=constant.LOGO_FILE_PATH
    )
    if (
        logo_resp == ""
        and constant.LOGO_FILE_PATH in files
        and files[constant.LOGO_FILE_PATH].filename != ""
    ):
        logo_file = files[constant.LOGO_FILE_PATH]
        if logo_file:
            logo_public_url = sh.upload_logo(
                bucket=bucket,
                logo_file=logo_file,
                bucket_name=doc[constant.BUCKET_NAME],
            )
            doc[constant.LOGO_FILE_PATH] = logo_public_url
    print("Before intent")
    intent_resp = validate_files_as_optional(
        files=files, file_type=constant.INTENT_FILE_PATH
    )
    print(intent_resp)
    print(
        intent_resp == ""
        and constant.INTENT_FILE_PATH in files
        and files[constant.INTENT_FILE_PATH].filename != ""
    )
    if (
        intent_resp == ""
        and constant.INTENT_FILE_PATH in files
        and files[constant.INTENT_FILE_PATH].filename != ""
    ):
        intent_file = files[constant.INTENT_FILE_PATH]
        if intent_file:
            doc[constant.INTENT_FILE_PATH] = sh.upload_intent(
                bucket=bucket,
                intent_file=intent_file,
                bucket_name=doc[constant.BUCKET_NAME],
            )
    fh.update_customer_by_id(doc_id=customer_id, doc_dict=doc)
    manage_customer_intents(customer_id)
    resp = jsonify({constant.MESSAGE: constant.CUSTOMER_UPDATED, constant.DATA: doc})
    print("Customer Updated.")
    return resp, status.HTTP_200_OK


@app.route(ROUTE, methods=["GET"])
@authorize()
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
        logo_file_path = data[constant.LOGO_FILE_PATH]
        bucket_name = data[constant.BUCKET_NAME]
        data[constant.LOGO_FILE_PATH] = sh.generate_download_signed_url_v4(
            bucket_name=bucket_name, blob_name=logo_file_path
        )
        if constant.INTENT_FILE_PATH in data.keys():
            data[constant.INTENT_FILE_PATH] = sh.generate_download_signed_url_v4(
                bucket_name=bucket_name, blob_name=data[constant.INTENT_FILE_PATH]
            )
        list_data.append(data)
    if len(list_data) != 0:
        resp = jsonify(list_data[0])
    else:
        resp = {}
    return resp, status.HTTP_200_OK


@app.route(ROUTE + "/<customer_id>", methods=["DELETE"])
@authorize()
def delete_customer(customer_id):
    """
    Delete customers data
    """
    doc = customer_id_validation(customer_id=customer_id)
    if not isinstance(doc, (dict)):
        return doc
    doc["is_deleted"] = True
    fh.update_customer_by_id(doc_id=customer_id, doc_dict=doc)
    resp = jsonify({constant.MESSAGE: constant.CUSTOMER_DELETED_MESSAGE_SUCCESS})
    resp.status_code = 200
    return resp


@app.route(ROUTE + "/status", methods=["PUT"])
@authorize()
def update_customer_status():
    """
    Update customers status
    """
    current_customer_id: any
    current_customer_doc: any
    new_customer_id: any
    new_customer_doc: any
    if (
        constant.CURRENT_CUSTOMER_ID in request.form.keys()
        and request.form[constant.CURRENT_CUSTOMER_ID] != ""
    ):
        current_customer_id = request.form[constant.CURRENT_CUSTOMER_ID]
        current_customer_doc = customer_id_validation(customer_id=current_customer_id)
        if not isinstance(current_customer_doc, (dict)):
            return current_customer_doc
        current_customer_doc[constant.STATUS] = False
    else:
        current_customer_doc = {}
    if (
        constant.NEW_CUSTOMER_ID in request.form.keys()
        and request.form[constant.NEW_CUSTOMER_ID] != ""
    ):
        new_customer_id = request.form[constant.NEW_CUSTOMER_ID]
        new_customer_doc = customer_id_validation(customer_id=new_customer_id)
        if not isinstance(new_customer_doc, (dict)):
            return new_customer_doc
        new_customer_doc[constant.STATUS] = True
    else:
        new_customer_doc = {}
    if len(current_customer_doc.keys()) != 0:
        fh.update_customer_by_id(
            doc_id=current_customer_id, doc_dict=current_customer_doc
        )
    if len(new_customer_doc.keys()) != 0:
        fh.update_customer_by_id(doc_id=new_customer_id, doc_dict=new_customer_doc)
    resp = jsonify({constant.MESSAGE: constant.CUSTOMER_STATUS_UPDATE_MESSAGE})
    resp.status_code = 200
    return resp


@app.route(ROUTE + "/<customer_id>/intent", methods=["POST"])
def manage_customer_intents(customer_id):
    """
    Add/Update/Delete customer intents
    """
    print("In manageIntentsForCustomer()")
    return intents.add_update_delete_intents(customer_id, "")


@app.route(ROUTE + "/<customer_id>/intent", methods=["GET"])
@authorize()
def get_customer_intents(customer_id):
    """
    Returns a list of customer intents
    """
    return intents.get_intents(customer_id, "")


@app.route(ROUTE + "/<customer_id>/intent/download", methods=["GET"])
@authorize()
def download_customer_intents(customer_id):
    """
    Downloads a CSV file of customer intents
    """
    return intents.download_to_csv(customer_id, "")
