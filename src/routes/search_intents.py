"""
Search Intent API
"""

import os, time, uuid, sys
from google.cloud import dialogflowcx_v3 as df
from flask import Flask, request

app = Flask(__name__)

ROUTE = "/detectIntent"
@app.route(ROUTE, methods=["POST"])

def detect_intent():
    '''
    Retuns the fulfillment text corresponding the intent
    '''
    project_id = os.environ["GCP_PROJECT"]
    location_id = "global"
    agent_id = ""
    agent = f"projects/{project_id}/locations/{location_id}/agents/{agent_id}"
    data = request.form
    #print(data['text_input'])
    text_input = data['text_input']
    try:
        text_input = text_input[:255] #dialog 
        DIALOGFLOW_LANGUAGE_CODE = "en"
        SESSION_ID = uuid.uuid4()
        session_path = f"{agent}/sessions/{SESSION_ID}"
        session_client = df.SessionsClient()
        text_input = df.TextInput(text=text_input)
        query_input = df.QueryInput(text=text_input, language_code=DIALOGFLOW_LANGUAGE_CODE)
        detectIntent = df.DetectIntentRequest(session=session_path,query_input=query_input)
        response = session_client.detect_intent(request=detectIntent)
        #print(response.query_result.intent.display_name)
        #print(response.query_result.response_messages)
        response_messages = [
        " ".join(msg.text.text) for msg in response.query_result.response_messages
        ]
        print(f"Response text: {' '.join(response_messages)}\n")
        return ''.join(response_messages)
    except:
        print("exception while input")
        print(text_input)
        print("Unexpected error:", sys.exc_info()[0])
        return "Error"
