"""
Google cloud storage file handler
"""
from operator import contains
import os
import time
from datetime import datetime, timezone, timedelta
from urllib import response
from google.cloud import storage
from google import auth
from google.auth.transport import requests
from src.helpers import constant

project_id = os.getenv(constant.PROJECT_ID,constant.DEFAULT_PROJECT_NAME)
audio_bucket_name=project_id+"_userflow_audio_backups"

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


def upload_logo(bucket, logo_file, bucket_name):
    """
    Create a new bucket in storage
    """
    timestamp = str(int(time.time())).split(".", maxsplit=1)[0]
    timestamp = timestamp + "_"
    file_name = "logo/" + timestamp + logo_file.filename
    logo_blob = bucket.blob(file_name)
    logo_blob.upload_from_string(logo_file.read(), content_type=logo_file.content_type)
    url = "gs://" + bucket_name + "/" + file_name
    return url


def upload_intent(bucket, intent_file, bucket_name):
    """
    Create a new bucket in storage
    """
    timestamp = str(int(time.time())).split(".", maxsplit=1)[0]
    timestamp = timestamp + "_"
    file_name = "intent/" + timestamp + intent_file.filename
    intent_blob = bucket.blob(file_name)
    intent_blob.upload_from_string(
        intent_file.read(), content_type=intent_file.content_type
    )
    url = "gs://" + bucket_name + "/" + file_name
    return url


def generate_download_signed_url_v4(bucket_name, blob_name):
    """Generates a v4 signed URL for downloading a blob.

    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """
    blob_name = (blob_name.split(bucket_name)[-1])
    if blob_name in "/":
        blob_name = blob_name[1:]
    credentials, project_id = auth.default()
    #token_refresh = requests.Request()
    #credentials.refresh(token_refresh)
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

def upload_audio_file(response,session_id):
    """
    Upload the audio file
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(audio_bucket_name)
    file_name = str(session_id)+".mp3"
    intent_blob = bucket.blob(file_name)
    metadata = { 'Cache-Control': 'public, max-age=0' }
    intent_blob.metadata = metadata
    intent_blob.upload_from_string(response)
