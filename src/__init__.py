"""
All Routes
"""
from flask import Flask
from flask_cors import CORS
from config import envConfig, gCloudConfig

app = Flask(__name__)

CORS(app)
cors = CORS(app, resources={r"/*": {"origins": envConfig.envVariables["cors"]["dev"]}})

from src.routes import health, user_search, customer
