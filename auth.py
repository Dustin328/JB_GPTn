from functools import wraps
from flask import request, jsonify
import jwt
import os
from datetime import datetime, timedelta
from models import User, get_db_session

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

def generate_token(user_id):
    """Generate a JWT token for a user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)  # Token expires in 7 days
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify a JWT token and return user_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        # Verify token
        user_id = verify_token(token)
        if user_id is None:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get user from database
        db = get_db_session()
        try:
            user = db.query(User).filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 401
            
            # Add user to kwargs
            kwargs['current_user'] = user
            return f(*args, **kwargs)
        finally:
            db.close()
    
    return decorated
