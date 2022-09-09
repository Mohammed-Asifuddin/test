import os
import csv
import traceback
from datetime import datetime
from flask import jsonify, send_file
from google.cloud import dialogflowcx_v3
from google.cloud.dialogflowcx_v3.types.intent import Intent, ListIntentsRequest
from google.protobuf.field_mask_pb2 import FieldMask
import firebase_admin
from firebase_admin import firestore
import gcsfs
from src.helpers import constant

# firebase_admin.initialize_app()
db = firestore.client()
client = dialogflowcx_v3.IntentsClient()
flows_client = dialogflowcx_v3.FlowsClient()
page_client = dialogflowcx_v3.PagesClient()

def get_masked_intent_ids(customer_id, product_id):
    """
    Returns the respective masked IDs stored in FS for the intents
    """
    intent_ids = {}
    if customer_id != "":
        docs = db.collection(constant.INTENT_COLLECTION).where(constant.CUSTOMER_ID, '==', customer_id).stream()
    elif product_id != "":
        docs = db.collection(constant.INTENT_COLLECTION).where(constant.PRODUCT_ID, '==', product_id).stream()
    for doc in docs:
        if doc.id:
            intent_ids[doc.id] = doc.to_dict()[constant.MASKED_INTENT_IDS]
    return intent_ids

def get_intents_data(intents, fullfillments):
    """
        Prepares and returns intents for a list of intent IDs
    """
    resp_intents = []
    # print(fullfillments)
    for intent in intents:
        if intent.display_name in ("Default Welcome Intent", "Default Negative Intent"):
            continue
        try:
            request = dialogflowcx_v3.GetIntentRequest(
                name= intent.name,
            )
            response = client.get_intent(request=request)
            # print(response)
        except Exception:
            print("There was an error while fetching an intent from DialogFlow!")
            traceback.print_exc()
            return "There was an error while fetching an intent from DialogFlow!"

        intent = {}
        intent_id = response.name.split(constant.STRING_INTENT_PATH)[1]
        intent[constant.MASKED_INTENT_IDS] = intent_id
        intent[constant.INTENT_DISPLAY_NAME] = response.display_name
        intent[constant.COLUMN_DESCRIPTION] = response.description
        phrases = []
        for phrase in response.training_phrases:
            phrase_dict = {}
            phrase_dict['repeat_count'] = phrase.repeat_count
            phrase_dict['id'] = phrase.id
            for part in phrase.parts:
                phrase_dict['parts'] = [{'text': part.text}]
            phrases.append(phrase_dict)
        intent[constant.INTENT_TRAINING_PHRASES] = phrases
        intent[constant.INTENT_FULFILLMENTS] = fullfillments[response.name]
        # print(intentDict)
        resp_intents.append(intent)
    return resp_intents

def get_all_product_pages(flow_path):
    request = dialogflowcx_v3.ListPagesRequest(
        parent=flow_path,
    )
    return page_client.list_pages(request=request)

def get_intents():
    """
    Returns a list of all intents for a specific customer/product
    """
    # print("In getIntents()")
    # agent_id = get_agent_id(customer_id, product_id)
    agent_id = "bb57d233-259b-4cfa-83ae-89db8dc688ee"
    # parent = f'projects/{PROJECT_ID}/locations/{constant.LOCATION_ID}/agents/{agent_id}'
    parent = f'projects/retail-btl-dev/locations/global/agents/{agent_id}'
    if (agent_id is None or agent_id == ''):
        resp = jsonify({"message": "No Agent found for this customer/product."})
        resp.status_code = 400
        return resp

    try:
        try:
            list_intents = ListIntentsRequest(parent=parent,page_size=1000)
            intents = client.list_intents(list_intents)

        except Exception:
            traceback.print_exc()
            print("No intents associated with this Agent ID!")
            resp = jsonify({"message": "No intents associated with this Agent ID!"})
            resp.status_code = 400
            return resp

        flow_path = f'{parent}/flows/{constant.DEFAULT_FLOW_ID}'
        flow_request = dialogflowcx_v3.GetFlowRequest(name=flow_path)
        flow = flows_client.get_flow(flow_request)
        # print(flow)
        fullfillments = {}
        for route in flow.transition_routes:
            print(route)
            if constant.DEFAULT_INTENT_ID not in route.intent:
                fullfillments[route.intent] = route.trigger_fulfillment.messages[0].text.text[0]

        #GET ALL PRODUCT PAGES
        product_id= "XYSD"
        if product_id!="":
            # product_name = get_product_name(product_id)
            product_name = "SPF30"
            pages = get_all_product_pages(flow_path)
            for page in pages:
                if page.display_name!=product_name:
                    continue
                for route in page.transition_routes:
                    print(route)
                    fullfillments[route.intent] = route.trigger_fulfillment.messages[0].text.text[0]

        resp_intents = get_intents_data(intents, fullfillments)
        # for resp_intent in resp_intents:
            # print(resp_intent[constant.MASKED_INTENT_IDS])
            # print(resp_intent[constant.INTENT_FULFILLMENTS])
            # print("------------------")

    except Exception:
        traceback.print_exc()
        print("There was an error while building intents response!")
        return "There was an error while building intents response!"

    print("Successfully retrieved intents: ", len(resp_intents))
    return resp_intents

get_intents()
