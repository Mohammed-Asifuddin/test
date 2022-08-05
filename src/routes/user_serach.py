from src import app
from flask_api import status
from flask import jsonify, request

from src.helpers.gCloud import vision_product_search

@app.route('/api/user/search', methods=['POST'])
def search_product():
    """
    User product search
    """
    # print(request.get_json())
    image_data = request.get_json()['imageFile']
    data = vision_product_search.get_similar_products_file(
        'retail-btl-dev', 'us-west1', 'PnG-manual-olay', 'packagedgoods-v1', image_data)
    print(data)
    resp_dict = {
        "productName": "Ford",
    }
    resp_dict['productName'] = data
    resp = jsonify(resp_dict)
    resp.status_code = 200
    return resp
