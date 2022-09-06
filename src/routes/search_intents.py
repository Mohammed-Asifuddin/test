"""
Search Intent API
"""

import os, time, uuid, sys
from google.cloud import dialogflowcx_v3 as df
from flask_cors import cross_origin
from flask import request
from src import app
from src.helpers import constant
from src.helpers.gCloud import firestore_helper as fsh
from flask_cors import cross_origin
from flask_api import status

ROUTE = "/detectIntent"


@app.route(ROUTE, methods=["POST"])
@cross_origin()
def detect_intent():
    """
    Returns the fulfillment text corresponding the intent
    """
    project_id = os.getenv(constant.PROJECT_ID, "retail-btl-uat")
    location_id = "global"

    data = request.json
    customer_id = data[constant.CUSTOMER_ID]
    text_input = data["text_input"]

    agent_id = fsh.get_agent_id_by_customer_id(customer_id)
    agent = f"projects/{project_id}/locations/{location_id}/agents/{agent_id}"

    try:
        text_input = text_input[:255]  # dialog
        DIALOGFLOW_LANGUAGE_CODE = "en"
        SESSION_ID = uuid.uuid4()
        session_path = f"{agent}/sessions/{SESSION_ID}"
        session_client = df.SessionsClient()
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
        return {"success": True, "fulfillments": response_messages}, status.HTTP_200_OK
    except Exception:
        print("exception while input")
        print(text_input)
        print("Unexpected error:", sys.exc_info()[0])
        return {
            "success": False,
            "message": "Error while getting fulfillments.",
        }, status.HTTP_400_BAD_REQUEST
