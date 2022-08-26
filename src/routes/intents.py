"""
Intent API service
"""
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

PROJECT_ID = "retail-btl-dev"
LOCATION_ID = "global"
DEFAULT_FLOW_ID = "00000000-0000-0000-0000-000000000000"
DEFAULT_INTENT_ID = "00000000-0000-0000"

firebase_admin.initialize_app()
db = firestore.client()
client = dialogflowcx_v3.IntentsClient()
flows_client = dialogflowcx_v3.FlowsClient()

def get_intent_path(customer_id, product_id):
    """
    Returns the path stored in FS where the intent file is located
    """
    if customer_id != "":
        doc = db.collection('Customer').document(customer_id).get()
    elif product_id != "":
        doc = db.collection('Product').document(product_id).get()
    if doc.id:
        return doc.to_dict()['intent_file_path']
    return ""

def get_agent_id(customer_id, product_id):
    """
    Returns the respective agent ID stored in FS for the customer/product
    """
    if customer_id != "":
        docs = db.collection('Agent').where('customer_id', '==', customer_id).stream()
    elif product_id != "":
        docs = db.collection('Agent').where('product_id', '==', product_id).stream()
    for doc in docs:
        if doc.id:
            return doc.to_dict()['agent_id']
    return ""

def get_masked_intent_ids(customer_id, product_id):
    """
    Returns the respective masked IDs stored in FS for the intents
    """
    intent_ids = {}
    if customer_id != "":
        docs = db.collection('Intent').where('customer_id', '==', customer_id).stream()
    elif product_id != "":
        docs = db.collection('Intent').where('product_id', '==', product_id).stream()
    for doc in docs:
        if doc.id:
            intent_ids[doc.id] = doc.to_dict()['maskedIntentId']
    return intent_ids

def get_actual_intent_ids(customer_id, product_id):
    """
    Returns the actual intent IDs stored in FS for the intents
    """
    intent_ids = {}
    if customer_id != "":
        docs = db.collection('Intent').where('customer_id', '==', customer_id).stream()
    elif product_id != "":
        docs = db.collection('Intent').where('product_id', '==', product_id).stream()
    for doc in docs:
        if doc.id:
            intent_ids[doc.to_dict()['maskedIntentId']] = doc.id
    return intent_ids

def create_intent(intent, parent, customer_id, product_id, agent_id):
    """
    Makes the call to dialogFLow create intent API
    """
    try:
        request = dialogflowcx_v3.CreateIntentRequest(
            parent=parent,
            intent=intent,
        )
        response = client.create_intent(request=request)
    except Exception:
        traceback.print_exc()
        resp = jsonify({"message": "Intent creation failed!"})
        resp.status_code = 400
        return resp

    intent_id = response.name.split("intents/")[1]
    intent_ref = db.collection('Intent').document(intent_id).set({
        'agent_id' : agent_id,
        'customer_id' : customer_id,
        'name' : intent.display_name,
        'product_id' : product_id,
        'maskedIntentId': datetime.now().strftime('%Y%m-%d%H-%M%S-') + intent_id[-4:]
    }, merge=True)
    print(intent_ref)
    return response

def update_intent(intent, intent_id):
    """
    Makes the call to dialogFLow update intent API
    """
    request = dialogflowcx_v3.UpdateIntentRequest(
        intent=intent,
    )
    try:
        response = client.update_intent(request=request)
    except Exception:
        traceback.print_exc()
        resp = jsonify({"message": "Intent updation failed!"})
        resp.status_code = 400
        return resp
    intent_name = response.display_name
    intent_id = response.name.split("intents/")[1]
    intent_ref = db.collection('Intent').document(intent_id).update({
        'name' : intent_name,
    })
    print(intent_ref)
    return response

def delete_intent(intent_id, parent):
    """
    Makes the call to dialogFLow delete intent API
    """
    try:
        request = dialogflowcx_v3.DeleteIntentRequest(
            name=f'{parent}/intents/{intent_id}',
        )
        client.delete_intent(request=request)
        db.collection('Intent').document(intent_id).delete()
    except Exception:
        traceback.print_exc()
        resp = jsonify({"message": "Intent deletion failed!"})
        resp.status_code = 400
        return resp
    return f'Intent {intent_id} deleted!'

def upsert_intent(intent_id, intent_name, intent_action, intent_desc, training_phrases, parent, customer_id, product_id, agent_id, fulfillments, intent_responses, intent_ids_to_delete):
    """
    Prepares the intent object to make the dialogFLow API calls
    """
    intent = dialogflowcx_v3.Intent()
    intent.display_name = intent_name
    intent.description = intent_desc

    phrases_array = []
    for phrase in training_phrases:
        part = Intent.TrainingPhrase.Part(text=phrase)
        phrases_array.append(Intent.TrainingPhrase(parts=[part], repeat_count=1))
    intent.training_phrases = phrases_array

    if intent_action=="Create":
        resp = create_intent(intent, parent, customer_id, product_id, agent_id)
    elif intent_action=="Update":
        intent.name = f'{parent}/intents/{intent_id}'
        resp = update_intent(intent, intent_id)
    elif intent_action=="Delete":
        intent_ids_to_delete.append(intent_id)
        return ""
    else:
        print("Invalid Action in CSV.")
        return ""
    if resp and resp.name != "":
        intent_responses[resp.name] = fulfillments
    return resp

def get_intents(customer_id, product_id):
    """
    Returns a list of all intents for a specific customer/product
    """
    print("In getIntents()")
    agent_id = get_agent_id(customer_id, product_id)
    parent = f'projects/{PROJECT_ID}/locations/{LOCATION_ID}/agents/{agent_id}'

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

        flow_path = f'{parent}/flows/{DEFAULT_FLOW_ID}'
        flow_request = dialogflowcx_v3.GetFlowRequest(name=flow_path)
        flow = flows_client.get_flow(flow_request)
        fullfillments = {}
        for route in flow.transition_routes:
            if DEFAULT_INTENT_ID not in route.intent:
                fullfillments[route.intent] = route.trigger_fulfillment.messages[0].text.text[0]

        resp_intents = []
        intent_ids = get_masked_intent_ids(customer_id, product_id)
        for intent in intents:
            if intent.display_name in ("Default Welcome Intent", "Default Negative Intent"):
                continue
            try:
                request = dialogflowcx_v3.GetIntentRequest(
                    name= intent.name,
                )
                response = client.get_intent(request=request)
                print(response)
            except Exception:
                print("There was an error while fetching an intent from DialogFlow!")
                traceback.print_exc()
                resp = jsonify({"message": "There was an error while fetching an intent from DialogFlow!"})
                resp.status_code = 400
                return resp

            intent = {}
            intent_id = response.name.split("intents/")[1]
            intent['maskedIntentId'] = "" if intent_ids.get(intent_id) is None else intent_ids.get(intent_id)
            intent['display_name'] = response.display_name
            intent['description'] = response.description
            phrases = []
            for phrase in response.training_phrases:
                phrase_dict = {}
                phrase_dict['repeat_count'] = phrase.repeat_count
                phrase_dict['id'] = phrase.id
                for part in phrase.parts:
                    phrase_dict['parts'] = [{'text': part.text}]
                phrases.append(phrase_dict)
            intent['training_phrases'] = phrases
            intent['fulfillments'] = fullfillments[response.name]
            # print(intentDict)
            resp_intents.append(intent)
        # print(intentArray)
    except Exception:
        traceback.print_exc()
        print("There was an error while building intents response!")
        resp = jsonify({"message": "There was an error while building intents response!"})
        resp.status_code = 400
        return resp

    print("Successfully retrieved intents: ", len(resp_intents))
    resp = jsonify({"intents": resp_intents})
    resp.status_code = 200
    return resp

def update_flow(flow, intents):
    """
    Updates the flow with all the intent routes
    """
    try:
        flow.transition_routes = [route for route in flow.transition_routes if DEFAULT_INTENT_ID in route.intent]
        for intent in intents:
            if DEFAULT_INTENT_ID in intent:
                continue
            res_text = dialogflowcx_v3.ResponseMessage.Text(text=[intents[intent]])
            resp_message = dialogflowcx_v3.ResponseMessage(text=res_text)
            fulfillment = dialogflowcx_v3.Fulfillment(messages=[resp_message])
            route = dialogflowcx_v3.TransitionRoute(intent=intent, trigger_fulfillment=fulfillment)
            flow.transition_routes.append(route)
        mask = FieldMask()
        mask.FromJsonString("transitionRoutes")
        flow_request = dialogflowcx_v3.UpdateFlowRequest(flow=flow, update_mask=mask)
        flows_client.update_flow(request=flow_request)
    except Exception:
        traceback.print_exc()
        print("There was an error while updating the flow!")
        resp = jsonify({"message": "There was an error while updating the flow!"})
        resp.status_code = 400
        return resp

def add_update_delete_intents(customer_id, product_id):
    """
    Iterates over the CSV to process the intents and routes appropriate intent API calls
    """
    agent_id = get_agent_id(customer_id, product_id)
    parent = f'projects/{PROJECT_ID}/locations/{LOCATION_ID}/agents/{agent_id}'

    if (agent_id is None or agent_id == ''):
        traceback.format_exc()
        resp = jsonify({"message": "No Agent found for this customer."})
        resp.status_code = 400
        return resp

    try:
        intent_path = get_intent_path(customer_id, product_id)
        gs_file_system = gcsfs.GCSFileSystem(project=PROJECT_ID)
        intent_ids = get_actual_intent_ids(customer_id, product_id)

        with gs_file_system.open(intent_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            training_phrases = []
            intent_id = ""
            intent_name = ""
            intent_action = ""
            intent_desc = ""
            fulfillments = ""
            response = ""
            intent_responses = {}
            intent_ids_to_delete = []
            for row in reader:
                if row['Action']=="":
                    training_phrases.append(row['Training Phrases'])
                else:
                    if training_phrases:
                        response = upsert_intent(intent_id, intent_name, intent_action, intent_desc, training_phrases, parent, customer_id, product_id, agent_id, fulfillments, intent_responses, intent_ids_to_delete)
                        print(response)
                        training_phrases.clear()
                    training_phrases.append(row['Training Phrases'])
                    if row['ID'] is None or row['ID']=='':
                        intent_id = ""
                    else:
                        intent_id = intent_ids[row['ID']]
                    intent_name, intent_desc, intent_action, fulfillments = row['Name'], row['Description'], row['Action'], row['Response']
            response = upsert_intent(intent_id, intent_name, intent_action, intent_desc, training_phrases, parent, customer_id, product_id, agent_id, fulfillments, intent_responses, intent_ids_to_delete)
            print(response)
            training_phrases.clear()

            #Updating the default start flow with all the intent routes
            intent_ids = get_actual_intent_ids(customer_id, product_id)
            flow_path = f'{parent}/flows/{DEFAULT_FLOW_ID}'
            flow_request = dialogflowcx_v3.GetFlowRequest(name=flow_path)
            flow = flows_client.get_flow(flow_request)
            print(intent_responses)
            update_flow(flow, intent_responses)

            #Deleting intents marked for deletion
            for intent_id in intent_ids_to_delete:
                delete_intent(intent_id, parent)

    except FileNotFoundError:
        traceback.print_exc()
        print("No Intents file found at the path.")
        resp = jsonify({"message": "No Intents file found at the path."})
        resp.status_code = 400
        return resp
    except Exception:
        traceback.print_exc()
        print("Customer/Product intents update failed!")
        resp = jsonify({"message": "Customer/Product intents update failed."})
        resp.status_code = 400
        return resp

    print("Customer/Product intents updated successfully.")
    resp = jsonify({"message": "Customer/Product intents updated successfully."})
    resp.status_code = 200
    return resp

def download_to_csv(customer_id, product_id):
    """
    Calls the get intent API, writes all the intents to the csv file and prompts the user to save it.
    """
    try:
        response = get_intents(customer_id, product_id)
        intents = response.json['intents']
        header = ['ID', 'Name', 'Description', 'Training Phrases', 'Response', 'Action']
        intent_path = f'/tmp/{customer_id}.csv'

        with open(intent_path, 'w',  encoding='UTF8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            data = []
            for intent in intents:
                phrases = intent['training_phrases']
                phrase = phrases[0]["parts"][0]["text"]
                data = [intent['maskedIntentId'], intent['display_name'], intent['description'], phrase, intent['fulfillments'], ""]
                writer.writerow(data)
                if len(phrases) > 1:
                    for phrase in phrases[1:]:
                        phrase_text = phrase["parts"][0]["text"]
                        data = ["", "", "", phrase_text, "", ""]
                        writer.writerow(data)

        return send_file(intent_path)
    except Exception:
        traceback.print_exc()
        print("There was an error while downloading intents CSV!")
        resp = jsonify({"message": "There was an error while downloading intents CSV!"})
        resp.status_code = 400
        return resp
