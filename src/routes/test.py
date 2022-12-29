
import os
from flask import Response, jsonify, request
from src import app


@app.route("/test", methods=["GET","POST"])
def search_product():
    return jsonify({"message":"This is test api"})

