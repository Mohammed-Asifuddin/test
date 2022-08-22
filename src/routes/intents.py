"""
Intent API service
"""
import csv
import traceback
from src import app
from flask import jsonify, request
from google.cloud import dialogflowcx_v3
from google.cloud.dialogflowcx_v3.services.intents import IntentsClient
from google.cloud.dialogflowcx_v3.types.intent import Intent, ListIntentsRequest
import firebase_admin
from firebase_admin import firestore
import gcsfs
from datetime import datetime

PROJECT_ID = "retail-btl-dev"
LOCATION_ID = "global"

firebase_admin.initialize_app()
db = firestore.client()
client = dialogflowcx_v3.IntentsClient()

def getIntentPath(customer_id, product_id):
    if customer_id != "":
        docs = db.collection(u'Customer').where(u'name', u'==',customer_id).stream()
    elif product_id != "":
        docs = db.collection(u'Product').where(u'name', u'==',product_id).stream()
    for doc in docs:
        if (doc.id):
            return doc.to_dict()['intent_file_path']
    return

def getAgentId(customer_id, product_id):
    if customer_id != "":
        docs = db.collection(u'Agent').where(u'customer_id', u'==',customer_id).stream()
    elif product_id != "":
        docs = db.collection(u'Agent').where(u'product_id', u'==',product_id).stream()
    for doc in docs:
        if (doc.id):
            return doc.to_dict()['agentId']
    return

def getMaskedIntentIds(customer_id, product_id):
    intentIdsDict = {}
    if customer_id != "":
        docs = db.collection(u'Intent').where(u'customer_id', u'==',customer_id).stream()
    elif product_id != "":
        docs = db.collection(u'Intent').where(u'product_id', u'==',product_id).stream()
    for doc in docs:
        if (doc.id):
            intentIdsDict[doc.id] = doc.to_dict()['maskedIntentId']
    return intentIdsDict

def getActualIntentIds(customer_id, product_id):
    intentIdsDict = {}
    if customer_id != "":
        docs = db.collection(u'Intent').where(u'customer_id', u'==',customer_id).stream()
    elif product_id != "":
        docs = db.collection(u'Intent').where(u'product_id', u'==',product_id).stream()
    for doc in docs:
        if (doc.id):
            intentIdsDict[doc.to_dict()['maskedIntentId']] = doc.id
    return intentIdsDict

def createIntent(intent, parent, customerId, productId, agentId):
    request = dialogflowcx_v3.CreateIntentRequest(
        parent=parent,
        intent=intent,
    )
    try:
        response = client.create_intent(request=request)
    except Exception as e:
        traceback.print_exc()
        resp = jsonify({"message": "Intent creation failed!"})
        resp.status_code = 400
        return resp

    intentId = response.name.split("intents/")[1]
    intent_ref = db.collection(u'Intent').document(intentId).set({
        u'agent_id' : agentId,
        u'customer_id' : customerId,
        u'name' : intent.display_name,
        u'product_id' : productId,
        u'maskedIntentId': datetime.now().strftime('%Y%m-%d%H-%M%S')
    }, merge=True)
    print(intent_ref)
    return response

def updateIntent(intent, intentId):
    request = dialogflowcx_v3.UpdateIntentRequest(
        intent=intent,
    )
    try:
        response = client.update_intent(request=request)
    except Exception as e:
        traceback.print_exc()
        resp = jsonify({"message": "Intent updation failed!"})
        resp.status_code = 400
        return resp
    intentName = response.display_name
    intentId = response.name.split("intents/")[1]
    intent_ref = db.collection(u'Intent').document(intentId).update({
        u'name' : intentName,
    })
    print(intent_ref)
    return response

def deleteIntent(intentId, parent):
    # Initialize request argument(s)
    print(intentId)
    try:
        request = dialogflowcx_v3.DeleteIntentRequest(
            name=f'{parent}/intents/{intentId}',
        )
        client.delete_intent(request=request)
        db.collection(u'Intent').document(intentId).delete()
    except Exception as e:
        traceback.print_exc()
        resp = jsonify({"message": "Intent deletion failed!"})
        resp.status_code = 400
        return resp
    return f'Intent {intentId} deleted!'

def upsertIntent(intentId, intentName, intentAction, intentDesc, trainingPhrases, parent, customerId, productId, agentId):
    intent = dialogflowcx_v3.Intent()
    intent.display_name = intentName
    intent.description = intentDesc
    
    phrasesArray = []
    for phrase in trainingPhrases:
        part = Intent.TrainingPhrase.Part(text=phrase)
        phrasesArray.append(Intent.TrainingPhrase(parts=[part], repeat_count=1))
    intent.training_phrases = phrasesArray
    
    if(intentAction=="Create"):
        return createIntent(intent, parent, customerId, productId, agentId)
    elif(intentAction=="Update"):
        intent.name = f'{parent}/intents/{intentId}'
        return updateIntent(intent, intentId)
    elif (intentAction=="Delete"):
        return deleteIntent(intentId, parent)
    else:
        print("Invalid Action in CSV.")

def getIntents(customer_id, product_id):
    print("In getIntents()")
    agentId = getAgentId(customer_id, product_id)
    parent = f'projects/{PROJECT_ID}/locations/{LOCATION_ID}/agents/{agentId}'

    if (agentId is None or agentId == ''):
        resp = jsonify({"message": "No Agent found for this customer/product."})
        resp.status_code = 400
        return resp

    try:
        try:
            listIntents = ListIntentsRequest(parent=parent,page_size=1000)
            intents = client.list_intents(listIntents)
        except:
            traceback.print_exc()
            print("No intents associated with this Agent ID!")
            resp = jsonify({"message": "No intents associated with this Agent ID!"})
            resp.status_code = 400
            return resp

        intentArray = []
        intentIds = getMaskedIntentIds(customer_id, product_id)
        for idx, intent in enumerate(intents):
            if intent.display_name == "Default Welcome Intent" or intent.display_name == "Default Negative Intent":
                continue
            try:
                request = dialogflowcx_v3.GetIntentRequest(
                    name= intent.name,
                )
                response = client.get_intent(request=request)
                print(response)
            except:
                print("There was an error while fetching an intent from DialogFlow!")
                traceback.print_exc()
                resp = jsonify({"message": "There was an error while fetching an intent from DialogFlow!"})
                resp.status_code = 400
                return resp
            
            intentDict = {}
            intentDict['maskedIntentId'] = intentIds[response.name.split("intents/")[1]]
            intentDict['display_name'] = response.display_name
            intentDict['description'] = response.description
            phrases = []
            for phrase in response.training_phrases:
                phraseDict = {}
                phraseDict['repeat_count'] = phrase.repeat_count
                phraseDict['id'] = phrase.id
                for part in phrase.parts:
                    phraseDict['parts'] = [{'text': part.text}]
                phrases.append(phraseDict)
            intentDict['training_phrases'] = phrases
            # print(intentDict)
            intentArray.append(intentDict)
        # print(intentArray)
    except:
        traceback.print_exc()
        print("There was an error while building intents response!")
        resp = jsonify({"message": "There was an error while building intents response!"})
        resp.status_code = 400
        return resp

    print("Successfully retrieved {} intents".format(idx+1))
    resp = jsonify({"intents": intentArray})
    resp.status_code = 200
    return resp

def addUpdateDeleteIntents(customer_id, product_id):
    
    agentId = getAgentId(customer_id, product_id)
    parent = f'projects/{PROJECT_ID}/locations/{LOCATION_ID}/agents/{agentId}'

    if (agentId is None or agentId == ''):
        traceback.format_exc()
        resp = jsonify({"message": "No Agent found for this customer."})
        resp.status_code = 400
        return resp
    
    try:
        intentPath = getIntentPath(customer_id, product_id)
        fs = gcsfs.GCSFileSystem(project=PROJECT_ID)
        intentIds = getActualIntentIds(customer_id, product_id)

        with fs.open(intentPath, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            trainingPhrases = []
            intentId = ""
            intentName = ""
            intentAction = ""
            intentDesc = ""
            response = ""
            for row in reader:
                if(row['Action']==""):
                    trainingPhrases.append(row['Training Phrases'])
                else:
                    if (trainingPhrases):
                        response = upsertIntent(intentId, intentName, intentAction, intentDesc, trainingPhrases, parent, customer_id, product_id, agentId)
                        print(response)
                        trainingPhrases.clear()
                    trainingPhrases.append(row['Training Phrases'])
                    if row['ID'] is None or row['ID']=='':
                        intentId = ""
                    else:
                        intentId = intentIds[row['ID']]
                    intentName, intentDesc, intentAction = row['Name'], row['Description'], row['Action']
            response = upsertIntent(intentId, intentName, intentAction, intentDesc, trainingPhrases, parent, customer_id, product_id, agentId)
            print(response)
            trainingPhrases.clear()
    except FileNotFoundError:
        traceback.print_exc()
        print("No Intents file found at the path.")
        resp = jsonify({"message": "No Intents file found at the path."})
        resp.status_code = 400
        return resp
    except:
        traceback.print_exc()
        print("Customer/Product intents update failed!")
        resp = jsonify({"message": "Customer/Product intents update failed."})
        resp.status_code = 400
        return resp

    print("Customer/Product intents updated successfully.")
    resp = jsonify({"message": "Customer/Product intents updated successfully."})
    resp.status_code = 200
    return resp
