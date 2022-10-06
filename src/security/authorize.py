"""
API Authorization service
"""
from functools import wraps
from firebase_admin import auth
from firebase_admin import firestore
from flask import abort,request

db = firestore.client()

def authorize():
    """
    Authorizes the user based on token and FS collection
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kws):
            if 'Authorization' not in request.headers:
                print("No header Authorization")
                abort(401)
            user = None
            # expected header `Authorization: Bearer <token>`
            data = request.headers['Authorization']
            auth_token = str(data)
            try:
                user = auth.verify_id_token(auth_token)
                user_details = db.collection('Users').where('email', '==', user['email']).where('is_active', '==', True).get()
                if len(user_details) <= 0:
                    print("ERROR: could not find user")
                    abort(401)
            except Exception as exp:
                print(exp)
                abort(401)
            return f(*args, **kws)
        return decorated_function
    return decorator
