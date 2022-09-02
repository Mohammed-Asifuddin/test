"""
File validator
"""
import time
from src.helpers.gCloud import storage_handler as sh

ALLOWED_IMAGE_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])
ALLOWED_VIDEO_EXTENSIONS = set(["mp4", "mov", "mp4v", "avi"])
ALLOWED_INTENT_EXTENSIONS = set(["csv"])


def allowed_image_file(filename):
    """
    Validate image file suffix.
    """
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    )


def allowed_video_file(filename):
    """
    Validate image file suffix.
    """
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS
    )


def allowed_intent_file(filename):
    """
    Validate intent file suffix.
    """
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_INTENT_EXTENSIONS
    )


def upload_video_file(customer_bucket_name, product_bucket_name, video_file_path):
    """
    Upload video file
    """
    bucket = sh.get_bucket_object_by_name(customer_bucket_name)
    timestamp = str(int(time.time())).split(".", maxsplit=1)[0]
    timestamp = timestamp + "_"
    file_name = (
        product_bucket_name + "/video/" + str(timestamp) + video_file_path.filename
    )
    video_file_blob = bucket.blob(file_name)
    video_file_blob.upload_from_string(
        video_file_path.read(), content_type=video_file_path.content_type
    )
    url = "gs://" + customer_bucket_name + "/" + file_name
    return url


def upload_intent_file(customer_bucket_name, product_bucket_name, intent_file_path):
    """
    Upload intent file
    """
    bucket = sh.get_bucket_object_by_name(customer_bucket_name)
    timestamp = str(int(time.time())).split(".", maxsplit=1)[0]
    timestamp = timestamp + "_"
    file_name = (
        product_bucket_name + "/intent/" + str(timestamp) + intent_file_path.filename
    )
    intent_file_blob = bucket.blob(file_name)
    intent_file_blob.upload_from_string(
        intent_file_path.read(), content_type=intent_file_path.content_type
    )
    intent_url = "gs://" + customer_bucket_name + "/" + file_name
    return intent_url
