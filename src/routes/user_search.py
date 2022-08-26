"""
User product search API module
"""
import os
from flask import jsonify, request
from src import app
from src.helpers.gCloud import vision_product_search as vps
from src.helpers.gCloud import firestore_helper as fh
from src.helpers import constant


@app.route("/api/user/search", methods=["POST"])
def search_product():
    """
    User product search Post Method
    """
    image_data = request.get_json()["imageFile"]
    # Get Active Customer Info
    active_customer = get_active_customer_info()
    print("*************************************")
    print(active_customer)
    print(type(active_customer))
    print("*************************************")
    product_categories = get_customer_product_categories(
        active_customer[constant.CUSTOMER_ID]
    )
    product_categories = [*set(product_categories)]
    # Get Active Customer Products Categories
    project_id = os.getenv("PROJECT_ID", "retail-btl-dev")
    location = "us-west1"
    data = vps.get_similar_products_file(
        project_id=project_id,
        location=location,
        product_set_id=active_customer[constant.BUCKET_NAME],
        product_categories=product_categories,
        image_uri=image_data,
    )
    print(data)
    resp_dict = {
        "productName": "Ford",
    }
    resp_dict["productName"] = data
    resp = jsonify(resp_dict)
    resp.status_code = 200
    return resp


def get_active_customer_info():
    """
    Get Active Customer Information
    """
    list_data = []
    docs = fh.get_active_customer()
    for doc in docs:
        data = doc.to_dict()
        data[constant.CUSTOMER_ID] = doc.id
        list_data.append(data)
    active_customer = {}
    print(list_data)
    if len(list_data) != 0:
        active_customer = list_data[0]
    print(active_customer)
    return active_customer


def get_customer_product_categories(customer_id):
    """
    Get All Customer products categories
    """
    docs = fh.get_all_products_by_customer_id(customer_id=customer_id)
    list_data = []
    for doc in docs:
        data = doc.to_dict()
        list_data.append(data[constant.CATEGORY_CODE])
    return list_data
