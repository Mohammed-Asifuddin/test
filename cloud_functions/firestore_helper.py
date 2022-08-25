"""
Fire store handler
"""
import os
from firebase_admin import firestore

db = firestore.Client(os.getenv("PROJECT_ID", "retail-btl-dev"))

TABLE_PRODUCT = "Product"
TABLE_TRAINING_DATA = "Training_Data"


def get_product_by_id(doc_id):
    """
    Get document by id
    """
    return db.collection(TABLE_PRODUCT).document(doc_id).get()

def add_training_data(td_dict):
    """
    Add a new row in training data
    """
    return db.collection(TABLE_TRAINING_DATA).add(td_dict)

def update_product_image_status(doc_id, doc_dict):
    """
    Update document by id
    """
    return db.collection(TABLE_PRODUCT).document(doc_id).set(doc_dict)
