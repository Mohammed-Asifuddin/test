"""
Video to image cloud function
"""
import os
import base64
import json
import cv2
from google.cloud import storage
import constant
import firestore_helper as fsh


def video_to_image(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    print("Pubsub message received and processing")
    pubsub_message = base64.b64decode(event["data"]).decode("utf-8")
    pubsub_message = json.loads(pubsub_message)
    video_name = (pubsub_message[constant.VIDEO_FILE_PATH].split("/"))[-1]
    doc = get_product_details(pubsub_message=pubsub_message)
    customer_bucket_name = doc[constant.CUSTOMER_BUCKET_NAME]
    product_bucket_name = doc[constant.PRODUCT_BUCKET_NAME]
    client = storage.Client()
    for blob in client.list_blobs(
        customer_bucket_name, prefix=product_bucket_name + "/video"
    ):
        if video_name in blob.name:
            print("Generating images")
            filename = blob.name.split("/")[-1]
            folder_name = filename.split(".")[0]
            filename = "/tmp/" + filename
            blob.download_to_filename(filename)
            captured = cv2.VideoCapture(filename)
            if captured.isOpened():
                success, image = captured.read()
                count = 0
                while success:
                    image_name = folder_name + "_frame_" + str(count) + ".jpg"
                    image_name2 = (
                        "/tmp/" + folder_name + "_frame_" + str(count) + ".jpg"
                    )
                    cv2.imwrite(image_name2, image)
                    bucket = client.bucket(customer_bucket_name)
                    img_blob = bucket.blob(
                        product_bucket_name
                        + "/training_data/"
                        + folder_name
                        + "/"
                        + image_name
                    )
                    img_blob.upload_from_filename(image_name2)
                    os.remove(image_name2)
                    success, image = captured.read()
                    count = count + 1
            captured.release()
            cv2.destroyAllWindows()
            os.remove(filename)
    print("Image generation is done.")
    td_dict = {}
    td_dict[constant.PRODUCT_ID] = pubsub_message[constant.PRODUCT_ID]
    td_dict[constant.TRAINING_IMAGE_PATH] = (
        customer_bucket_name
        + "/"
        + product_bucket_name
        + "/training_data/"
        + folder_name
    )
    td_dict[constant.IS_TRAINED] = False
    td_dict[constant.IS_IMPORTED] = False
    td_dict[constant.VISION_REF_PATH] = ""
    fsh.add_training_data(td_dict=td_dict)
    print("saved row in training data")
    doc[constant.IMAGE_STATUS] = True
    fsh.update_product_image_status(
        doc_id=pubsub_message[constant.PRODUCT_ID], doc_dict=doc
    )
    print("updated product document")


def get_product_details(pubsub_message):
    """
    Get Product details
    """
    return fsh.get_product_by_id(doc_id=pubsub_message[constant.PRODUCT_ID]).to_dict()
