"""
All Routes
"""
from flask import Flask
from flask_cors import CORS
from config import envConfig, gCloudConfig

app = Flask(__name__)

CORS(app)

from src.routes import health, user_search, customer, product, product_training
