import os
from flask import Response, jsonify, request
from src import app
from firebase_admin import firestore
db = firestore.Client(os.getenv("PROJECT_ID","DEFAULT_PROJECT_NAME"))

@app.route("/getData", methods=["GET","POST"])
def get_data():
    return db.collection("User Details").document("ra6s2VUAxb8RkDsGGOad").get().to_dict()
