"""
ML Training helper
"""
import os
from flask_cors import cross_origin
from flask_api import status
from flask import request, jsonify
import cv2
from src import app
from src.helpers import constant
from src.helpers.gCloud import firestore_helper as fsh
from google.cloud import storage


@app.route("/generate/images", methods=["POST"])
@cross_origin()
def generate_images():
    """
    Generate images
    """
    doc = fsh.get_product_by_id(request.get_json()[constant.PRODUCT_ID]).to_dict()
    customer_bucket_name = doc[constant.CUSTOMER_BUCKET_NAME]
    product_bucket_name = doc[constant.PRODUCT_BUCKET_NAME]
    client = storage.Client()
    for blob in client.list_blobs(
        customer_bucket_name, prefix=product_bucket_name + "/video"
    ):
        filename = blob.name.split("/")[-1]
        folder_name = filename.split(".")[0]
        blob.download_to_filename(filename)
        captured = cv2.VideoCapture(filename)
        if captured.isOpened():
            print("Read")
            success, image = captured.read()
            count = 0
            while success:
                image_name = folder_name + "_frame_" + str(count) + ".jpg"
                cv2.imwrite(image_name, image)
                bucket = client.bucket(customer_bucket_name)
                img_blob = bucket.blob(
                    product_bucket_name + "/training_data/" + image_name
                )
                img_blob.upload_from_filename(image_name)
                os.remove(image_name)
                success, image = captured.read()
                count = count + 1
        captured.release()
        cv2.destroyAllWindows()
        os.remove(filename)
    resp = jsonify({constant.MESSAGE: "Images generated successfully"})
    return resp, status.HTTP_200_OK

@app.route("/generate/csv", methods=["POST"])
@cross_origin()
def generate_csv():
    """
    Generate images
    """
    doc = fsh.get_product_by_id(request.get_json()[constant.PRODUCT_ID]).to_dict()
    customer_bucket_name = doc[constant.CUSTOMER_BUCKET_NAME]
    product_bucket_name = doc[constant.PRODUCT_BUCKET_NAME]
    client = storage.Client()
    for blob in client.list_blobs(
        customer_bucket_name, prefix=product_bucket_name + "/training_data"
    ):
        image_gs_path = "gs://"+str(blob.name)
        #row = f"gs://{bucket_name}/{blob.name},,PnG-manual-olay,{productId},packagedgoods-v1,{[*data.values()][0]},\"{labelRow}\",\n" 
        row = f"{image_gs_path},,{doc[constant.CUSTOMER_BUCKET_NAME]},{doc[constant.PRODUCT_ID]}, {doc[constant.CATEGORY_NAME]}"
        print(row)
    resp = jsonify({constant.MESSAGE: "CSV generated successfully"})
    return resp, status.HTTP_200_OK
