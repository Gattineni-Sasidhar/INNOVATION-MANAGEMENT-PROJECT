import jwt
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "super-secret-key-for-qsf" # in a real app this would be in .env

def generate_token(user_id: int, role: str) -> str:
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
            
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
            
        payload = decode_token(token)
        if not payload:
            return jsonify({'message': 'Token is invalid or expired!'}), 401
            
        return f(payload['user_id'], *args, **kwargs)
    return decorated
    
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
            
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
            
        payload = decode_token(token)
        if not payload or payload.get('role') != 'admin':
            return jsonify({'message': 'Admin access required!'}), 403
            
        return f(payload['user_id'], *args, **kwargs)
    return decorated
