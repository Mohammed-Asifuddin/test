from src import app
from flask_api import status

route = "/api/health"

# @type: GET
# @description: check if api is running
# @access: public 
# @url: /api/health/running 

@app.route(route + "/running", methods=['get'])
def healthCheck():
    return {
        "success": True,
        "message": "Api is running"
    }, status.HTTP_200_OK