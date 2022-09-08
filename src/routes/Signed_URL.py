"""
Signed URL Router
"""

from flask_cors import cross_origin
from flask_api import status
from flask import request, jsonify
from src import app
from src.helpers import constant
from src.helpers.gCloud import storage_handler as sh
from src.security.authorize import authorize

@app.route("/signed-url", methods=["POST"])
@cross_origin()
@authorize()
def generate_signed_url():
    """
    Generated Signed URL for gs util path
    """
    print(request.get_json().keys())
    bucket_name = ""
    blob_name = ""
    if constant.CUSTOMER_BUCKET_NAME in request.get_json().keys():
        bucket_name = request.get_json()[constant.CUSTOMER_BUCKET_NAME]
        if bucket_name.strip() == "":
            resp = jsonify(
                {constant.MESSAGE: "Customer Bucket Name is not blank."})
            return resp, status.HTTP_400_BAD_REQUEST
    else:
        resp = jsonify(
            {constant.MESSAGE: "Customer Bucket Name is mandatory."})
        return resp, status.HTTP_400_BAD_REQUEST
    if constant.BLOB_NAME in request.get_json().keys():
        blob_name = request.get_json()[constant.BLOB_NAME]
        if blob_name.strip() == "":
            resp = jsonify({constant.MESSAGE: "Blob Name is not blank."})
            return resp, status.HTTP_400_BAD_REQUEST
    else:
        resp = jsonify({constant.MESSAGE: "Blob Name is mandatory."})
        return resp, status.HTTP_400_BAD_REQUEST
    url = sh.generate_download_signed_url_v4(
        bucket_name=bucket_name, blob_name=blob_name)
    resp = jsonify(
        {constant.MESSAGE: "Signed URL generated successfully.", constant.DATA: url})
    return resp, status.HTTP_200_OK
