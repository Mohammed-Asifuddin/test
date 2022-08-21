"""
Google cloud storage file handler
"""
import time
from google.cloud import storage

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
    timestamp = str(int(time.time())).split('.', maxsplit=1)[0]
    timestamp = timestamp + "_"
    logo_blob = bucket.blob('logo/'+timestamp+logo_file.filename)
    logo_blob.upload_from_string(logo_file.read(), content_type=logo_file.content_type)
    return logo_blob.public_url

def upload_intent(bucket, intent_file):
    """
    Create a new bucket in storage
    """
    timestamp = str(int(time.time())).split('.', maxsplit=1)[0]
    timestamp = timestamp + "_"
    intent_blob = bucket.blob("intent/"+timestamp+intent_file.filename)
    intent_blob.upload_from_string(intent_file.read(), content_type=intent_file.content_type)
    return intent_blob.public_url
