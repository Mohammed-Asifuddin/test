"""
Product API Request Validations
"""
from flask import jsonify
from src.routes import customer
from src.helpers.gCloud import firestore_helper as fsh
from src.helpers import constant


def validate_create_request(create_request):
    """
    Validate all required fields
    """
    customer_id_resp = validate_customer_id(customer_id_request=create_request)
    if customer_id_resp != "":
        return customer_id_resp
    category_id_resp = validate_category_id(category_id_request=create_request)
    if category_id_resp != "":
        return category_id_resp
    name_resp = validate_name(name_request=create_request)
    if name_resp != "":
        return name_resp
    label_resp = validate_label(label_request=create_request)
    if label_resp != "":
        return label_resp
    description_resp = validate_description(description_request=create_request)
    if description_resp != "":
        return description_resp
    product_files = create_request.files
    video_file_path_resp = customer.validate_files_as_mandatory(
        files=product_files, file_type=constant.VIDEO_FILE_PATH
    )
    if video_file_path_resp != "":
        return video_file_path_resp
    intent_file_path_resp = customer.validate_files_as_optional(
        files=product_files, file_type=constant.INTENT_FILE_PATH
    )
    if intent_file_path_resp != "":
        return intent_file_path_resp
    return ""


def validate_customer_id(customer_id_request):
    """
    Customer Id Validate
    """
    if constant.CUSTOMER_ID not in customer_id_request.form.keys():
        resp = jsonify({constant.MESSAGE: constant.CUSTOMER_MANDATORY})
        resp.status_code = 400
        return resp
    customer_id = customer_id_request.form[constant.CUSTOMER_ID]
    if customer_id.strip() == "":
        resp = jsonify({constant.MESSAGE: constant.CUSTOMER_BLANK_MESSAGE})
        resp.status_code = 400
        return resp
    doc = customer.customer_id_validation(customer_id=customer_id)
    if not isinstance(doc, (dict)):
        resp = jsonify({constant.MESSAGE: constant.CUSTOMER_NO_DATA_MESSAGE})
        resp.status_code = 400
        return resp
    return ""


def validate_category_id(category_id_request):
    """
    Category Id Validate
    """
    if constant.CATEGORY_ID not in category_id_request.form.keys():
        resp = jsonify({constant.MESSAGE: constant.CATEGORY_ID_MANDATORY})
        resp.status_code = 400
        return resp
    category_id = category_id_request.form[constant.CATEGORY_ID]
    if category_id.strip() == "":
        resp = jsonify({constant.MESSAGE: constant.CATEGORY_NOT_BLANK})
        resp.status_code = 400
        return resp
    docs = fsh.get_product_category_by_id(category_id=category_id)
    if not docs.exists:
        resp = jsonify({constant.MESSAGE: constant.CATEGORY_NO_DATA})
        resp.status_code = 400
        return resp
    doc = docs.to_dict()
    if not isinstance(doc, (dict)):
        resp = jsonify({constant.MESSAGE: constant.CATEGORY_NO_DATA})
        resp.status_code = 400
        return resp
    return ""


def validate_name(name_request):
    """
    Name field Validation
    """
    if constant.NAME not in name_request.form.keys():
        resp = jsonify({constant.MESSAGE: constant.NAME_MANDATORY})
        resp.status_code = 400
        return resp
    name = name_request.form[constant.NAME]
    if name.strip() == "":
        resp = jsonify({constant.MESSAGE: constant.NAME_NOT_BLANK})
        resp.status_code = 400
        return resp
    return ""


def validate_label(label_request):
    """
    Label field Validation
    """
    if constant.LABEL not in label_request.form.keys():
        resp = jsonify({constant.MESSAGE: constant.LABEL_MANDATORY})
        resp.status_code = 400
        return resp
    label = label_request.form[constant.LABEL]
    if label.strip() == "":
        resp = jsonify({constant.MESSAGE: constant.LABEL_NOT_BLANK})
        resp.status_code = 400
        return resp
    return ""


def validate_description(description_request):
    """
    Description field Validation
    """
    if constant.DESCRIPTION not in description_request.form.keys():
        resp = jsonify({constant.MESSAGE: constant.DESCRIPTION_MANDATORY})
        resp.status_code = 400
        return resp
    description = description_request.form[constant.DESCRIPTION]
    if description.strip() == "":
        resp = jsonify({constant.MESSAGE: constant.DESCRIPTION_NOT_BLANK})
        resp.status_code = 400
        return resp
    return ""


def is_duplicate_product(product_bucket_name):
    """
    Is product duplicate
    """
    doc_id_list = fsh.get_product_category_by_product_bucket_name(product_bucket_name)
    if len(doc_id_list) == 0:
        return len(doc_id_list)
    resp = jsonify({constant.MESSAGE: constant.PRODUCT_EXISTS})
    resp.status_code = 400
    return resp


def validate_update_request(update_request):
    """
    Update request validator
    """
    product_id_resp = validate_product_id(product_id_request=update_request)
    if product_id_resp != "":
        return product_id_resp
    return ""


def validate_product_id(product_id_request):
    """
    Product Id Validate
    """
    if constant.PRODUCT_ID not in product_id_request.form.keys():
        resp = jsonify({constant.MESSAGE: constant.PRODUCT_ID_MANDATORY})
        resp.status_code = 400
        return resp
    product_id = product_id_request.form[constant.PRODUCT_ID]
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
    return ""
