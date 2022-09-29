"""
User product search API module
"""
import os
from flask import jsonify, request, Response
from flask_cors import cross_origin
from src import app
from src.helpers.gCloud import vision_product_search as vps
from src.helpers.gCloud import firestore_helper as fh
from src.helpers import constant
from src.helpers.gCloud import secret_manager_helper as smh
from src.security.authorize import authorize
from src.helpers.gCloud import text_to_speech_helper as ts
from src.helpers.gCloud import storage_handler as sh


@app.route("/api/user/search", methods=["POST"])
@cross_origin()
@authorize()
def search_product():
    """
    User product search Post Method
    """
    image_data = request.get_json()["imageFile"]
    print('Image:')
    print(image_data)
    active_customer = get_active_customer_info()
    if active_customer:
        product_categories = get_customer_product_categories(
            active_customer[constant.CUSTOMER_ID]
        )
        product_categories = [*set(product_categories)]
        project_id = os.getenv(constant.PROJECT_ID,
                               constant.DEFAULT_PROJECT_NAME)
        location = "us-west1"
        response = vps.get_similar_products_file(
            project_id=project_id,
            location=location,
            product_set_id=active_customer[constant.BUCKET_NAME],
            product_categories=product_categories,
            image_uri=image_data,
        )
        if hasattr(response, 'error'):
            resp = jsonify({constant.MESSAGE: response.error.message})
            resp.status_code = 400
            return resp
        if hasattr(response, 'score') and response.score >= 0.65:
            product_id = response.product.product_labels[0].value
            doc = fh.get_product_by_id(doc_id=product_id).to_dict()
            doc[constant.PRODUCT_ID] = product_id
            resp = jsonify(
                {constant.MESSAGE: "Product identified.", constant.DATA: doc})
            resp.status_code = 200
        else:
            resp = jsonify(
                {constant.MESSAGE: "Product not found"})
            resp.status_code = 400
        return resp
    resp = jsonify({constant.MESSAGE: "No Active Customer"})
    resp.status_code = 400
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
    if len(list_data) != 0:
        active_customer = list_data[0]
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


@app.route("/api/token", methods=["GET"])
def get_user_details():
    """
    Provides username and password details
    """
    resp = jsonify({constant.MESSAGE: "Success",
                   constant.TOKEN: smh.get_user_flow_token()})
    return resp


@app.route("/api/text-to-speech", methods=["POST"])
@cross_origin()
@authorize()
def convert_text_to_speech():
    """
    Provides username and password details
    """
    session_id = request.headers.get('session_id')
    if session_id == "" or session_id.strip() == "":
        resp = jsonify({constant.MESSAGE: "Unidentified user."})
        resp.status_code = 400
        return resp
    text = request.get_json()["text"]
    if text == "" or text.strip() == "":
        resp = jsonify({constant.MESSAGE: "Text is mandatory"})
        resp.status_code = 400
        return resp
    response = ts.convert_text_to_speech(text)
    url = sh.upload_audio_file(response=response,session_id=session_id)
    #return Response(response,mimetype="audio/x-wav")
    resp = jsonify({constant.MESSAGE: "Success","audio_file_url": url})
    return resp
