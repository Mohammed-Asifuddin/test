"""
secret manager helper service
"""
import json
import os
import requests
from google.cloud import secretmanager
from src.helpers import constant
from src.helpers.gCloud import firestore_helper as fsh

project_id = os.getenv(constant.PROJECT_ID, constant.DEFAULT_PROJECT_NAME)
REST_API_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
VERSION_ID = "latest"


def get_user_flow_token():
    """
    This method get user flow user from secret manger and validate the user and provides the token
    """
    secret_id = get_user_flow_sm_key()
    user_flow_user_sm_value = get_secret_value(secret_id=secret_id)
    token_bytes = get_user_flow_user_token(
        user_info_str=user_flow_user_sm_value)
    token = token_bytes['idToken']
    return token


def get_user_flow_sm_key():
    """
    Get configured secret id from fire store
    """
    docs = fsh.get_configuration()
    configuration = {}
    for doc in docs:
        data = doc.to_dict()
        configuration = {**data, **configuration}
    return configuration[constant.SM_KEY_UF]


def get_user_flow_user_token(user_info_str):
    """
    Create a custom token for user flow api user.
    """
    user_info = json.loads(user_info_str)
    api_key = get_secret_value("FIREBASE_WEB_API_KEY")
    payload = json.dumps({
        "email": user_info['username'],
        "password": user_info['password'],
        "returnSecureToken": True
    })
    resp = requests.post(REST_API_URL, params={"key": api_key}, data=payload)
    results = resp.json()
    return results


def get_secret_value(secret_id):
    """
    The secret value based on key
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{VERSION_ID}"
    resp = client.access_secret_version(request={"name": name})
    return resp.payload.data.decode("UTF-8")
