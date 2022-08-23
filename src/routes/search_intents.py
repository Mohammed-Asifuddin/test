import os, time, uuid, sys
from google.cloud import dialogflowcx_v3 as df

project_id = "retail-btl-dev"
location_id = "global"
agent_id = "15e6ae3c-301e-4802-a22c-45fe62107658"

agent = f"projects/{project_id}/locations/{location_id}/agents/{agent_id}"

def detect_intent(agent, text_input):
    try:
        text_input = text_input[:255] #dialog 
        DIALOGFLOW_LANGUAGE_CODE = "en"
        SESSION_ID = uuid.uuid4()
        session_path = f"{agent}/sessions/{SESSION_ID}"
        #print(session_path)
        session_client = df.SessionsClient()
        #print(session_client)
        text_input = df.TextInput(text=text_input)
        #print(text_input)
        query_input = df.QueryInput(text=text_input, language_code=DIALOGFLOW_LANGUAGE_CODE)
        #print(query_input)
        detectIntent = df.DetectIntentRequest(session=session_path,query_input=query_input)
        #print(detect_intent)
        response = session_client.detect_intent(request=detectIntent)
        #print(response)
        #print(response.query_result.intent.display_name)
        #print(response.query_result.response_messages)
        response_messages = [
        " ".join(msg.text.text) for msg in response.query_result.response_messages
        ]
        print(f"Response text: {' '.join(response_messages)}\n")
    except:
        print("exception while input")
        print(text_input)
        print("Unexpected error:", sys.exc_info()[0])
        return ""

detect_intent(f"projects/{project_id}/locations/{location_id}/agents/{agent_id}", "Does this contain microbeads?")
