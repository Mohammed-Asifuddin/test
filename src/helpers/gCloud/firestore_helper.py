"""
Fire store handler
"""
import os
from firebase_admin import firestore
from src.helpers import constant

db = firestore.Client(os.getenv(constant.PROJECT_ID,constant.DEFAULT_PROJECT_NAME))

TABLE_CUSTOMER = "Customer"
TABLE_PRODUCT = "Product"
TABLE_PRODUCT_CATEGORY = "Product_Category"
TABLE_AGENT = "Agent"
TABLE_CONFIGURATION = "Configuration"
EQUAL_OPERATOR = "=="
TABLE_TRAINING_DATA = "Training_Data"


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


def get_configuration():
    """
    Fetch configuration data
    """
    return db.collection(TABLE_CONFIGURATION).stream()


def get_non_imported_products():
    """
    Get all untrained products
    """
    return (
        db.collection(TABLE_TRAINING_DATA)
        .where(constant.IS_IMPORTED, EQUAL_OPERATOR, False)
        .stream()
    )


def get_non_trained_products():
    """
    Get all untrained products
    """
    return (
        db.collection(TABLE_TRAINING_DATA)
        .where(constant.IS_TRAINED, EQUAL_OPERATOR, False)
        .stream()
    )


def get_non_imported_products_by_id(product_id):
    """
    Get all untrained products
    """
    return (
        db.collection(TABLE_TRAINING_DATA)
        .where(constant.IS_IMPORTED, EQUAL_OPERATOR, False)
        .where(constant.PRODUCT_ID, EQUAL_OPERATOR, product_id)
        .stream()
    )


def get_non_trained_products_by_id(product_id):
    """
    Get all untrained products
    """
    return (
        db.collection(TABLE_TRAINING_DATA)
        .where(constant.IS_TRAINED, EQUAL_OPERATOR, False)
        .where(constant.PRODUCT_ID, EQUAL_OPERATOR, product_id)
        .stream()
    )


def update_training_data_by_id(doc_id, doc_dict):
    """
    Update document by id
    """
    return db.collection(TABLE_TRAINING_DATA).document(doc_id).set(doc_dict)


def get_all_products_by_customer_id(customer_id):
    """
    Get all products related to customer by id
    """
    return (
        db.collection(TABLE_PRODUCT)
        .where(constant.CUSTOMER_ID, EQUAL_OPERATOR, customer_id)
        .stream()
    )


def get_agent_id_by_customer_id(customer_id):
    """
    Returns the respective agent ID stored in FS for the customer
    """
    docs = ""
    if customer_id != "":
        docs = (
            db.collection(TABLE_AGENT)
            .where(constant.CUSTOMER_ID, "==", customer_id)
            .stream()
        )
    for doc in docs:
        if doc.id:
            return doc.to_dict()[constant.AGENT_ID]
    return ""
