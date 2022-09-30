"""
Signed URL Router
"""
import os
from flask_cors import cross_origin
from flask_api import status
from flask import request, jsonify
from src import app
from src.helpers import constant
from src.helpers.gCloud import storage_handler as sh
from src.security.authorize import authorize

project_id = os.getenv(constant.PROJECT_ID,constant.DEFAULT_PROJECT_NAME)
audio_bucket_name=project_id+"_userflow_audio_backups"

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


@app.route("/api/audio-signed-url", methods=["POST"])
@cross_origin()
@authorize()
def generate_signed_url_for_audio_file():
    """
    Generated Signed URL for gs util path
    """
    print(request.get_json().keys())
    blob_name = ""
    if constant.AUDIO_SESSION_ID in request.get_json().keys():
        blob_name = request.get_json()[constant.AUDIO_SESSION_ID]
        if blob_name.strip() == "":
            resp = jsonify({constant.MESSAGE: "Session Id is not blank."})
            return resp, status.HTTP_400_BAD_REQUEST
    else:
        resp = jsonify({constant.MESSAGE: "Session Id is mandatory."})
        return resp, status.HTTP_400_BAD_REQUEST
    blob_name = blob_name+".mp3"
    url = sh.generate_download_signed_url_v4(bucket_name=audio_bucket_name, blob_name=blob_name)
    resp = jsonify({constant.MESSAGE: "Audio Signed URL generated successfully.", constant.DATA: url})
    return resp, status.HTTP_200_OK
