"""
All Routes
"""
import os
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from config import envConfig, gCloudConfig


app = Flask(__name__)

# Swagger configurations
swagger_config = {
    "headers": [],
    "specs": [{"endpoint": "documentacao_api", "route": "/documentacao_api.json"}],
    "static_url_path": "/flasgger_static",
    "specs_route": "/api/docs/",
}

app.config["SWAGGER"] = {
    "title": "Beyond The Label - APIs",
    # 'uiversion': 2
}
swagger = Swagger(app, config=swagger_config, template_file='swagger.yml')
# end of swagger configuration

CORS(app)

from src.routes import (
    health,
    user_search,
    customer,
    product,
    product_training,
    search_intents,
)
