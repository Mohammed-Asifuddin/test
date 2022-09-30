"""
Search Intent API
"""

from cgitb import text
import os
import time
import uuid
import sys
from google.cloud import dialogflowcx_v3 as df
from flask_cors import cross_origin
from flask import request
from flask_api import status
from src import app
from src.helpers import constant
from src.helpers.gCloud import firestore_helper as fsh
from src.security.authorize import authorize
from src.helpers.gCloud import text_to_speech_helper as ts
from src.helpers.gCloud import storage_handler as sh

ROUTE = "/detectIntentNew"

session_client = df.SessionsClient()


def detect_intent(agent, session_id, text_input):
    try:
        text_input = text_input[:255]  # dialog
        DIALOGFLOW_LANGUAGE_CODE = "en"

        session_path = f"{agent}/sessions/{session_id}"
        print(session_path)
        text_input = df.TextInput(text=text_input)
        query_input = df.QueryInput(
            text=text_input, language_code=DIALOGFLOW_LANGUAGE_CODE
        )
        detect_intent_request = df.DetectIntentRequest(
            session=session_path, query_input=query_input
        )
        response = session_client.detect_intent(request=detect_intent_request)
        # print(response.query_result.intent.display_name)
        # print(response.query_result.response_messages)
        response_messages = [
            " ".join(msg.text.text) for msg in response.query_result.response_messages
        ]
        print(f"Response text: {' '.join(response_messages)}\n")
        speech_text = response_messages[0]
        audi_response = ts.convert_text_to_speech(speech_text)
        sh.upload_audio_file(response=audi_response, session_id=session_id)
        return {"success": True, "fulfillments": response_messages, "uuid": session_id}, status.HTTP_200_OK
    except Exception:
        print("exception while input")
        print(text_input)
        print("Unexpected error:", sys.exc_info()[0])
        return {
            "success": False,
            "message": "Error while getting fulfillments.",
        }, status.HTTP_400_BAD_REQUEST


@app.route(ROUTE, methods=["POST"])
@cross_origin()
@authorize()
def prepare_detect_intent():
    """
    Returns the fulfillment text corresponding the intent
    """
    project_id = os.getenv(constant.PROJECT_ID, constant.DEFAULT_PROJECT_NAME)
    location_id = "global"

    data = request.json
    customer_id = data[constant.CUSTOMER_ID]
    text_input = data["text_input"]
    session_id = data["session_id"]
    product_name = data["product_name"]

    agent_id = fsh.get_agent_id_by_customer_id(customer_id)
    agent = f"projects/{project_id}/locations/{location_id}/agents/{agent_id}"

    if session_id != "":
        SESSION_ID = session_id
    else:
        SESSION_ID = uuid.uuid4()
        # Initializing Dialogflow pages.
        detect_intent(agent, SESSION_ID, "Hi")
        detect_intent(agent, SESSION_ID, product_name)

    resp = detect_intent(agent, SESSION_ID, text_input)
    print(resp)
    return resp
