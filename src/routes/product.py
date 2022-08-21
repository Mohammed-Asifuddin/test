"""
Product API service
"""
import time
from flask_api import status
from flask import request, jsonify
from src import app
from src.helpers import product_valid as pv
from src.helpers.gCloud import firestore_helper as fsh
from src.helpers import file_validator as fv
from src.routes import customer
from src.helpers import constant

ROUTE = "/product"


@app.route(ROUTE, methods=["POST"])
def add_product():
    """
    Add new product
    """
    product_dict = {}
    validate_resp = pv.validate_create_request(create_request=request)
    if validate_resp == "":
        product_name = request.form["name"]
        product_bucket_name = "".join(
            char for char in product_name if char.isalnum()
        ).lower()
        product_duplicate = pv.is_duplicate_product(
            product_bucket_name=product_bucket_name
        )
        if product_duplicate == 0:
            customer_id = request.form[constant.CUSTOMER_ID]
            product_dict[constant.CUSTOMER_ID] = customer_id
            product_dict["name"] = request.form["name"]
            product_dict["label"] = request.form["label"]
            product_dict["description"] = request.form["description"]
            product_dict["category_id"] = request.form["category_id"]
            product_dict["metadata"] = request.form["metadata"]
            product_dict["image_status"] = 0
            product_dict["training_status"] = 0
            product_dict["is_deleted"] = False
            product_dict["product_display_id"] = str(int(time.time())).split(
                ".", maxsplit=1
            )[0]
            product_dict["product_bucket_name"] = product_bucket_name
            doc = fsh.get_customer_by_id(customer_id).to_dict()
            customer_bucket_name = doc["bucket_name"]
            product_dict["customer_bucket_name"] = customer_bucket_name
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
            new_doc = fsh.add_product(product_dict=product_dict)
            product_dict["product_id"] = new_doc[-1].id
        else:
            return product_duplicate
    else:
        return validate_resp
    resp = jsonify(
        {constant.MESSAGE: "Customer created successfully", "data": product_dict}
    )
    return resp, status.HTTP_201_CREATED


@app.route(ROUTE, methods=["PUT"])
def update_product():
    """
    Update product
    """
    product_id_resp = pv.validate_update_request(update_request=request)
    if product_id_resp != "":
        return product_id_resp
    product_id = request.form["product_id"]
    is_updated = False
    doc = fsh.get_product_by_id(doc_id=product_id).to_dict()
    if "label" in request.form.keys() and request.form["label"].strip() != "":
        doc["label"] = request.form["label"]
        is_updated = True
    if (
        "description" in request.form.keys()
        and request.form["description"].strip() != ""
    ):
        doc["description"] = request.form["description"]
        is_updated = True
    if "metadata" in request.form.keys() and request.form["metadata"].strip() != "":
        doc["metadata"] = request.form["metadata"]
        is_updated = True
    video_file_path_resp = customer.validate_files_as_optional(
        files=request.files, file_type=constant.VIDEO_FILE_PATH
    )
    if video_file_path_resp == "":
        video_file = request.files[constant.VIDEO_FILE_PATH]
        if video_file:
            video_file_public_url = fv.upload_video_file(
                customer_bucket_name=doc["customer_bucket_name"],
                product_bucket_name=doc["product_bucket_name"],
                video_file_path=video_file,
            )
            doc[constant.VIDEO_FILE_PATH] = video_file_public_url
            is_updated = True
    else:
        return video_file_path_resp
    intent_file_path_resp = customer.validate_files_as_optional(
        files=request.files, file_type=constant.INTENT_FILE_PATH
    )
    if intent_file_path_resp == "":
        intent_file = request.files[constant.INTENT_FILE_PATH]
        if intent_file:
            intent_file_public_url = fv.upload_intent_file(
                customer_bucket_name=doc["customer_bucket_name"],
                product_bucket_name=doc["product_bucket_name"],
                intent_file_path=intent_file,
            )
            doc[constant.INTENT_FILE_PATH] = intent_file_public_url
            is_updated = True
    else:
        return intent_file_path_resp
    if is_updated:
        fsh.update_product_by_id(doc_id=product_id, doc_dict=doc)
    resp = jsonify({constant.MESSAGE: "Product updated successfully", "data": doc})
    return resp, status.HTTP_200_OK


@app.route(ROUTE, methods=["GET"])
def get_all_products():
    """
    Get all products data
    """
    list_data = []
    docs = fsh.get_all_products()
    for doc in docs:
        data = doc.to_dict()
        data["product_id"] = doc.id
        list_data.append(data)
    resp = jsonify(list_data)
    return resp, status.HTTP_200_OK


@app.route(ROUTE + "/<product_id>", methods=["DELETE"])
def delete_product(product_id):
    """
    Delete customers data
    """
    if product_id.strip() == "":
        resp = jsonify({constant.MESSAGE: "product_id is neither empty nor blank"})
        resp.status_code = 400
        return resp
    docs = fsh.get_product_by_id(doc_id=product_id)
    if not docs.exists:
        resp = jsonify({constant.MESSAGE: "No data found with given product_id"})
        resp.status_code = 400
        return resp
    doc = docs.to_dict()
    if not isinstance(doc, (dict)):
        resp = jsonify({constant.MESSAGE: "No data found for given product_id."})
        resp.status_code = 400
        return resp
    doc["is_deleted"] = True
    fsh.update_product_by_id(doc_id=product_id, doc_dict=doc)
    resp = jsonify({constant.MESSAGE: "Product deleted successfully"})
    resp.status_code = 200
    return resp
