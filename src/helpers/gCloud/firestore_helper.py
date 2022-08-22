"""
Fire store handler
"""
import os
from firebase_admin import firestore
from src.helpers import constant

db = firestore.Client(os.getenv("PROJECT_ID", "retail-btl-dev"))

TABLE_CUSTOMER = "Customer"
TABLE_PRODUCT = "Product"
TABLE_PRODUCT_CATEGORY = "Product_Category"
TABLE_AGENT = "Agent"
EQUAL_OPERATOR = "=="


def get_customer_by_bucket_name(bucket_name):
    """
    Get customer by name
    """
    docs = (
        db.collection(TABLE_CUSTOMER)
        .where(constant.BUCKET_NAME, EQUAL_OPERATOR, bucket_name)
        .stream()
    )
    doc_id_list = []
    for doc in docs:
        doc_id_list.append(doc.id)
    return doc_id_list


def add_customer(customer_dict):
    """
    Add new customer
    """
    return db.collection(TABLE_CUSTOMER).add(customer_dict)


def get_customer_by_id(doc_id):
    """
    Get document by id
    """
    return db.collection(TABLE_CUSTOMER).document(doc_id).get()


def update_customer_by_id(doc_id, doc_dict):
    """
    Update document by id
    """
    return db.collection(TABLE_CUSTOMER).document(doc_id).set(doc_dict)


def get_all_customers():
    """
    Return All customers
    """
    return (
        db.collection(TABLE_CUSTOMER)
        .where(constant.IS_DELETED, EQUAL_OPERATOR, False)
        .stream()
    )


def get_active_customer():
    """
    Return All customers
    """
    return (
        db.collection(TABLE_CUSTOMER)
        .where(constant.IS_DELETED, EQUAL_OPERATOR, False)
        .where(constant.STATUS, EQUAL_OPERATOR, True)
        .stream()
    )


def get_product_category_by_id(category_id):
    """
    Get product category by id
    """
    return db.collection(TABLE_PRODUCT_CATEGORY).document(category_id).get()


def get_product_category_by_product_bucket_name(product_bucket_name):
    """
    Get product category by id
    """
    docs = (
        db.collection(TABLE_PRODUCT)
        .where(constant.PRODUCT_BUCKET_NAME, EQUAL_OPERATOR, product_bucket_name)
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
    return db.collection(TABLE_PRODUCT).add(product_dict)


def get_all_products():
    """
    Return All products
    """
    return (
        db.collection(TABLE_PRODUCT)
        .where(constant.IS_DELETED, EQUAL_OPERATOR, False)
        .stream()
    )


def get_product_by_id(doc_id):
    """
    Get document by id
    """
    return db.collection(TABLE_PRODUCT).document(doc_id).get()


def update_product_by_id(doc_id, doc_dict):
    """
    Update document by id
    """
    return db.collection(TABLE_PRODUCT).document(doc_id).set(doc_dict)


def add_agent(agent_dict):
    """
    Add new Agent
    """
    return db.collection(TABLE_AGENT).add(agent_dict)


def get_all_product_categories():
    """
    Return All product categories
    """
    return db.collection(TABLE_PRODUCT_CATEGORY).stream()
