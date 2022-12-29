
import os
from flask import Flask
from flask_cors import CORS
import firebase_admin

app = Flask(__name__)
CORS(app)

firebase_admin.initialize_app()
from src.routes import (
    test,getData,g
)

@app.route('/')
def hello_world():
    return 'Hello World'


