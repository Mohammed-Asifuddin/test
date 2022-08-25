"""
ML Training helper
"""

from operator import contains
from urllib import request
from flask_cors import cross_origin
from flask_api import status
from flask import request, jsonify
from google.cloud import storage
from src import app
from src.helpers import constant
from src.helpers.gCloud import firestore_helper as fsh


@app.route("/product-training", methods=["POST"])
@cross_origin()
def generate_csv():
    """
    Generate CSV
    """
    product_id = ""
    if request and request.is_json:
        product_id = request.get_json()[constant.PRODUCT_ID]
    products = []
    if product_id != "":
        products = get_all_training_required_products_by_id(product_id=product_id)
    else:
        products = get_all_training_required_products()
    # Group by product ids
    products_by_id = group_products_by_id(products=products)
    # Generate CSV
    for product in products_by_id:
        generate_csv_using_images_path(
            product_id=product, training_paths=products_by_id[product_id]
        )
    # TODO : Send import request to vision
    resp = jsonify({constant.MESSAGE: "Product training initiated successfully."})
    return resp, status.HTTP_200_OK


def get_all_training_required_products():
    """
    Get All import false documents
    """
    docs = fsh.get_non_imported_products()
    list_td_dict = []
    for doc in docs:
        data = doc.to_dict()
        data["TD_ID"] = doc.id
        list_td_dict.append(data)
    # print(list_td_dict)
    return list_td_dict


def get_all_training_required_products_by_id(product_id):
    """
    Get All import false documents by product id
    """
    docs = fsh.get_non_imported_products_by_id(product_id=product_id)
    list_td_dict = []
    for doc in docs:
        data = doc.to_dict()
        data["TD_ID"] = doc.id
        list_td_dict.append(data)
    # print(list_td_dict)
    return list_td_dict


def group_products_by_id(products):
    """
    Group products by id
    """
    result = {}
    for dct in products:
        result.setdefault(dct[constant.PRODUCT_ID], []).append(dct)
    # print(result)
    return result


def generate_csv_using_images_path(product_id, training_paths):
    """
    Generate CSV and upload to GCS
    """
    print("Preparing CSV data")
    doc = fsh.get_product_by_id(doc_id=product_id).to_dict()
    customer_bucket_name = doc[constant.CUSTOMER_BUCKET_NAME]
    product_bucket_name = doc[constant.PRODUCT_BUCKET_NAME]
    product_name = doc[constant.NAME]
    category_name = doc[constant.CATEGORY_CODE]
    client = storage.Client()
    rows = ""
    for training_path_dict in training_paths:
        training_path = training_path_dict["training_images_path"]
        for blob in client.list_blobs(
            customer_bucket_name, prefix=product_bucket_name + "/training_data"
        ):
            # print(blob.name)
            image_path = "gs://" + customer_bucket_name + "/" + blob.name
            if training_path in image_path:
                row = f"{image_path},,{customer_bucket_name},{product_id},{category_name},{product_name},,\n"
                rows = rows + row
    #print(rows)
    print("CSV data prepared and saving into gcs")
    bucket = client.get_bucket(customer_bucket_name)
    blob = bucket.blob('csv/'+customer_bucket_name+'.csv')
    blob.upload_from_string(rows)
    print(blob.path)
    print(blob.self_link)
    print('CSV Generated and uploaded')
