"""
GCP pubsub helper
"""
import os
import json
from google.cloud import pubsub_v1
from src.helpers import constant
from src.helpers.gCloud import firestore_helper as fsh


def push_to_pubsub(product_id, video_file_path):
    """
    Push notification into pubsub topic
    """
    project_id = os.getenv("PROJECT_ID", "retail-btl-uat")
    topic_id = get_topic_id_video_to_image()
    data_dict = {}
    data_dict[constant.PRODUCT_ID] = product_id
    data_dict[constant.VIDEO_FILE_PATH] = video_file_path
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    data = json.dumps(data_dict).encode("utf-8")
    publisher.publish(topic_path, data)

def get_topic_id_video_to_image():
    """
    Video to image pubsub topic id
    """
    configuration = {}
    docs = fsh.get_configuration()
    for doc in docs:
        data = doc.to_dict()
        configuration = {**data, **configuration}
    return configuration[constant.PUBSUB_VIDEO_TO_IMAGE_TOPIC_ID]
