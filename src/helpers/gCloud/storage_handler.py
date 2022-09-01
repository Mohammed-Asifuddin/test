"""
Google cloud storage file handler
"""
import time
from datetime import datetime, timezone, timedelta
from google.cloud import storage
from google import auth
from google.auth.transport import requests


def create_bucket(bucket_name):
    """
    Create a new bucket in storage
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    new_bucket = storage_client.create_bucket(bucket)
    return new_bucket


def get_bucket_object_by_name(bucket_name):
    """
    Get a new bucket object from storage
    """
    storage_client = storage.Client()
    return storage_client.bucket(bucket_name)


def upload_logo(bucket, logo_file):
    """
    Create a new bucket in storage
    """
    timestamp = str(int(time.time())).split(".", maxsplit=1)[0]
    timestamp = timestamp + "_"
    logo_blob = bucket.blob("logo/" + timestamp + logo_file.filename)
    logo_blob.upload_from_string(logo_file.read(), content_type=logo_file.content_type)
    return logo_blob.public_url


def upload_intent(bucket, intent_file):
    """
    Create a new bucket in storage
    """
    timestamp = str(int(time.time())).split(".", maxsplit=1)[0]
    timestamp = timestamp + "_"
    intent_blob = bucket.blob("intent/" + timestamp + intent_file.filename)
    intent_blob.upload_from_string(
        intent_file.read(), content_type=intent_file.content_type
    )
    return intent_blob.public_url


def generate_download_signed_url_v4(bucket_name, blob_name):
    """Generates a v4 signed URL for downloading a blob.

    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """
    blob_name = (blob_name.split(bucket_name)[-1])[1:]
    credentials, project_id = auth.default()
    token_refresh = requests.Request()
    credentials.refresh(token_refresh)
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.get_blob(blob_name)
    if blob:
        now = datetime.now(timezone.utc)
        expiration = now + timedelta(minutes=90)
        url = blob.generate_signed_url(
            version="v4",
            expiration=expiration,
            method="GET",
            service_account_email=credentials.service_account_email,
            access_token=credentials.token,
        )
    else:
        url = None
    return url
