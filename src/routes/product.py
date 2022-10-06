"""
Product API service
"""
import os
import time
from flask_cors import cross_origin
from flask_api import status
from flask import request, jsonify
from src import app
from src.helpers import product_valid as pv
from src.helpers.gCloud import firestore_helper as fsh
from src.helpers import file_validator as fv
from src.routes import customer, intents
from src.helpers import constant
from src.helpers.gCloud import pubsub_helper as psh
from src.helpers.gCloud import dialogflow as df
from src.security.authorize import authorize
from src.helpers.gCloud import vision_product_search as vps

PROJECT_ID_VALUE = os.getenv(
    constant.PROJECT_ID, constant.DEFAULT_PROJECT_NAME)

ROUTE = "/product"


@app.route(ROUTE, methods=["POST"])
@cross_origin()
@authorize()
def add_product():
    """
    Add new product
    """
    product_dict = {}
    validate_resp = pv.validate_create_request(create_request=request)
    if validate_resp != "":
        return validate_resp
    product_name = request.form[constant.NAME]
    product_bucket_name = "".join(
        char for char in product_name if char.isalnum()
    ).lower()
    product_duplicate = pv.is_duplicate_product(
        product_bucket_name=product_bucket_name
    )
    if product_duplicate != 0:
        return product_duplicate
    customer_id = request.form[constant.CUSTOMER_ID]
    product_dict[constant.CUSTOMER_ID] = customer_id
    product_dict[constant.NAME] = request.form[constant.NAME]
    product_dict[constant.LABEL] = request.form[constant.LABEL]
    product_dict[constant.DESCRIPTION] = request.form[constant.DESCRIPTION]
    product_dict[constant.CATEGORY_ID] = request.form[constant.CATEGORY_ID]
    product_dict[constant.METADATA] = request.form[constant.METADATA]
    product_dict[constant.IMAGE_STATUS] = 0
    product_dict[constant.TRAINING_STATUS] = 0
    product_dict[constant.IS_DELETED] = False
    product_dict["product_display_id"] = str(int(time.time())).split(
        ".", maxsplit=1
    )[0]
    product_dict[constant.PRODUCT_BUCKET_NAME] = product_bucket_name
    doc = fsh.get_customer_by_id(customer_id).to_dict()
    customer_bucket_name = doc[constant.BUCKET_NAME]
    product_dict[constant.CUSTOMER_BUCKET_NAME] = customer_bucket_name
    product_dict[constant.CUSTOMER_NAME] = doc[constant.NAME]
    category_doc = fsh.get_product_category_by_id(
        category_id=request.form[constant.CATEGORY_ID]
    ).to_dict()
    product_dict[constant.CATEGORY_NAME] = category_doc[constant.CATEGORY]
    product_dict[constant.CATEGORY_CODE] = category_doc[constant.CATEGORY_CODE]
    video_file_path = request.files[constant.VIDEO_FILE_PATH]
    product_dict[constant.VIDEO_FILE_PATH] = fv.upload_video_file(
        customer_bucket_name=customer_bucket_name,
        product_bucket_name=product_bucket_name,
        video_file_path=video_file_path,
    )
    if (
        constant.INTENT_FILE_PATH in request.files
        and request.files[constant.INTENT_FILE_PATH]
        and request.files[constant.INTENT_FILE_PATH].filename != ""
    ):
        intent_file_path = request.files[constant.INTENT_FILE_PATH]
        product_dict[constant.INTENT_FILE_PATH] = fv.upload_intent_file(
            customer_bucket_name=customer_bucket_name,
            product_bucket_name=product_bucket_name,
            intent_file_path=intent_file_path,
        )

    # Create New Page for the product
    agent_id = fsh.get_agent_id_by_customer_id(customer_id)
    new_product_page = df.create_product_page(agent_id, product_name)
    product_dict[constant.PRODUCT_PAGE_ID] = new_product_page.name.split(
        "/")[-1]

    # Link product page to Default/anchor product page
    anchor_product_page_id = fsh.get_anchor_product_page(customer_id)
    resp = df.add_route_for_product_name_page(
        agent_id, anchor_product_page_id, new_product_page)
    print(resp)

    new_doc = fsh.add_product(product_dict=product_dict)
    product_dict[constant.PRODUCT_ID] = new_doc[-1].id
    if constant.INTENT_FILE_PATH in product_dict:
        intent_response = manage_product_intents(
            product_dict[constant.PRODUCT_ID])
        if intent_response.status_code == 400:
            intent_response = intent_response.json
            intent_response.update({constant.DATA: product_dict})
            resp = jsonify(intent_response)
            resp.status_code = 400
            return resp
    psh.push_to_pubsub(
        product_id=product_dict[constant.PRODUCT_ID],
        video_file_path=product_dict[constant.VIDEO_FILE_PATH],
    )
    resp = jsonify(
        {constant.MESSAGE: constant.PRODUCT_ADD_MESSAGE, constant.DATA: product_dict}
    )
    return resp, status.HTTP_201_CREATED


@app.route(ROUTE, methods=["PUT"])
@cross_origin()
@authorize()
def update_product():
    """
    Update product
    """
    product_id_resp = pv.validate_update_request(update_request=request)
    if product_id_resp != "":
        return product_id_resp
    product_id = request.form[constant.PRODUCT_ID]
    doc = fsh.get_product_by_id(doc_id=product_id).to_dict()
    if (
        constant.LABEL in request.form.keys()
        and request.form[constant.LABEL].strip() != ""
    ):
        doc[constant.LABEL] = request.form[constant.LABEL]
    if (
        constant.DESCRIPTION in request.form.keys()
        and request.form[constant.DESCRIPTION].strip() != ""
    ):
        doc[constant.DESCRIPTION] = request.form[constant.DESCRIPTION]
    if (
        constant.METADATA in request.form.keys()
        and request.form[constant.METADATA].strip() != ""
    ):
        doc[constant.METADATA] = request.form[constant.METADATA]
    video_file_path_resp = customer.validate_files_as_optional(
        files=request.files, file_type=constant.VIDEO_FILE_PATH
    )
    if (
        video_file_path_resp == ""
        and constant.VIDEO_FILE_PATH in request.files
        and request.files[constant.VIDEO_FILE_PATH].filename.strip() != ""
    ):
        video_file_public_url = fv.upload_video_file(
            customer_bucket_name=doc[constant.CUSTOMER_BUCKET_NAME],
            product_bucket_name=doc[constant.PRODUCT_BUCKET_NAME],
            video_file_path=request.files[constant.VIDEO_FILE_PATH],
        )
        doc[constant.VIDEO_FILE_PATH] = video_file_public_url
        doc[constant.IMAGE_STATUS] = False
        doc[constant.TRAINING_STATUS] = 0
        psh.push_to_pubsub(
            product_id=product_id,
            video_file_path=doc[constant.VIDEO_FILE_PATH],
        )

    intent_file_path_resp = customer.validate_files_as_optional(
        files=request.files, file_type=constant.INTENT_FILE_PATH
    )
    if (
        intent_file_path_resp == ""
        and constant.INTENT_FILE_PATH in request.files
        and request.files[constant.INTENT_FILE_PATH].filename.strip() != ""
    ):
        intent_file_public_url = fv.upload_intent_file(
            customer_bucket_name=doc[constant.CUSTOMER_BUCKET_NAME],
            product_bucket_name=doc[constant.PRODUCT_BUCKET_NAME],
            intent_file_path=request.files[constant.INTENT_FILE_PATH],
        )
        doc[constant.INTENT_FILE_PATH] = intent_file_public_url
    fsh.update_product_by_id(doc_id=product_id, doc_dict=doc)
    if constant.INTENT_FILE_PATH in doc:
        intent_response = manage_product_intents(product_id)
        if intent_response.status_code == 400:
            intent_response = intent_response.json
            intent_response.update({constant.DATA: doc})
            resp = jsonify(intent_response)
            resp.status_code = 400
            return resp
    resp = jsonify(
        {constant.MESSAGE: constant.PRODUCT_UPDATE_MESSAGE, constant.DATA: doc}
    )
    return resp


@app.route(ROUTE, methods=["GET"])
@authorize()
def get_all_products():
    """
    Get all products data
    """
    list_data = []
    docs = fsh.get_all_products()
    for doc in docs:
        data = doc.to_dict()
        data[constant.PRODUCT_ID] = doc.id
        list_data.append(data)
    resp = jsonify(list_data)
    return resp, status.HTTP_200_OK


@app.route(ROUTE + "/<product_id>", methods=["DELETE"])
@authorize()
def delete_product(product_id):
    """
    Delete product data
    """
    if product_id.strip() == "":
        resp = jsonify({constant.MESSAGE: constant.PRODUCT_EMPTY_OR_BLANK})
        resp.status_code = 400
        return resp
    docs = fsh.get_product_by_id(doc_id=product_id)
    if not docs.exists:
        resp = jsonify({constant.MESSAGE: constant.PRODUCT_NO_DATA})
        resp.status_code = 400
        return resp
    doc = docs.to_dict()
    if not isinstance(doc, (dict)):
        resp = jsonify({constant.MESSAGE: constant.PRODUCT_NO_DATA})
        resp.status_code = 400
        return resp
    doc["is_deleted"] = True
    fsh.update_product_by_id(doc_id=product_id, doc_dict=doc)
    delete_vision_product(product_id=product_id)
    resp = jsonify({constant.MESSAGE: constant.PRODUCT_DELETE_MESSAGE})
    resp.status_code = 200
    return resp


@app.route(ROUTE + "/categories", methods=["GET"])
@authorize()
def get_all_products_categories():
    """
    Get all products data
    """
    list_data = []
    docs = fsh.get_all_product_categories()
    for doc in docs:
        data = doc.to_dict()
        data[constant.CATEGORY_ID] = doc.id
        list_data.append(data)
    resp = jsonify(list_data)
    return resp, status.HTTP_200_OK


@app.route(ROUTE + "/<product_id>/intent", methods=["POST"])
@authorize()
def manage_product_intents(product_id):
    """
    Add/Update/Delete product intents
    """
    print("In manageIntentsForProduct()")
    return intents.add_update_delete_intents("", product_id)


@app.route(ROUTE + "/<product_id>/intent", methods=["GET"])
@authorize()
def get_product_intents(product_id):
    """
    Returns a list of product intents
    """
    return intents.get_intents("", product_id)


@app.route(ROUTE + "/<product_id>/intent/download", methods=["GET"])
@authorize()
def download_product_intents(product_id):
    """
    Downloads a CSV file of product intents
    """
    return intents.download_to_csv("", product_id)


def delete_vision_product(product_id):
    """
    Delete products Id
    """
    vps.delete_product(project_id=PROJECT_ID_VALUE,
                       location=constant.US_WEST_1, product_id=product_id)
