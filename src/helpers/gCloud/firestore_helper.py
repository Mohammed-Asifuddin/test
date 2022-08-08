"""
Fire store handler
"""
import os
from firebase_admin import firestore

db = firestore.Client(os.getenv("PROJECT_ID", "retail-btl-dev"))

def get_customer_by_bucket_name(bucket_name):
    """
    Get customer by name
    """
    docs =  db.collection("Customer").where("bucket_name", "==", bucket_name).stream()
    doc_id_list=[]
    for doc in docs:
        doc_id_list.append(doc.id)
    return doc_id_list
def add_customer(customer_dict):
    """
    Add new customer
    """
    return db.collection("Customer").add(customer_dict)
