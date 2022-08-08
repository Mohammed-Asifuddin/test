"""
API Health
"""
from flask_api import status
from src import app


ROUTE = "/api/health"

@app.route(ROUTE + "/running", methods=["get"])
def health_check():
    """
    check if api is running
    @url: /api/health/running
    """
    return {"success": True, "message": "Api is running"}, status.HTTP_200_OK
