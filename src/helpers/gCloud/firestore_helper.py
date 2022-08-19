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
    docs = db.collection("Customer").where("bucket_name", "==", bucket_name).stream()
    doc_id_list = []
    for doc in docs:
        doc_id_list.append(doc.id)
    return doc_id_list


def add_customer(customer_dict):
    """
    Add new customer
    """
    return db.collection("Customer").add(customer_dict)


def get_customer_by_id(doc_id):
    """
    Get document by id
    """
    return db.collection("Customer").document(doc_id).get()


def update_customer_by_id(doc_id, doc_dict):
    """
    Update document by id
    """
    return db.collection("Customer").document(doc_id).set(doc_dict)


def get_all_customers():
    """
    Return All customers
    """
    return db.collection("Customer").where("is_deleted", "==", False).stream()


def get_all_product_category():
    """
    Return All product categories
    """
    return db.collection("Product_Category").stream()


def get_product_category_by_id(category_id):
    """
    Get product category by id
    """
    return db.collection("Product_Category").document(category_id).get()


def get_product_category_by_product_bucket_name(product_bucket_name):
    """
    Get product category by id
    """
    docs = (
        db.collection("Product")
        .where("product_bucket_name", "==", product_bucket_name)
        .stream()
    )
    doc_id_list = []
    for doc in docs:
        doc_id_list.append(doc.id)
    return doc_id_list

def add_product(product_dict):
    """
    Add new customer
    """
    return db.collection("Product").add(product_dict)

def get_all_products():
    """
    Return All products
    """
    return db.collection("Product").where("is_deleted", "==", False).stream()

def get_product_by_id(doc_id):
    """
    Get document by id
    """
    return db.collection("Product").document(doc_id).get()

def update_product_by_id(doc_id, doc_dict):
    """
    Update document by id
    """
    return db.collection("Product").document(doc_id).set(doc_dict)
