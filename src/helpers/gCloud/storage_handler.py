"""
Google cloud storage file handler
"""
from google.cloud import storage


def create_bucket(bucket_name):
    """
    Create a new bucket in storage
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    new_bucket = storage_client.create_bucket(bucket)
    return new_bucket

def upload_logo(bucket, logo_file):
    """
    Create a new bucket in storage
    """
    logo_blob = bucket.blob("logo/"+logo_file.filename)
    logo_blob.upload_from_string(logo_file.read(), content_type=logo_file.content_type)
    return logo_blob.public_url

def upload_intent(bucket, intent_file):
    """
    Create a new bucket in storage
    """
    intent_blob = bucket.blob("intent/"+intent_file.filename)
    intent_blob.upload_from_string(intent_file.read(), content_type=intent_file.content_type)
    return intent_blob.public_url
