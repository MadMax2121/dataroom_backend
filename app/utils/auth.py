import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from app.models.user import User

def generate_token(user_id):
    """Generate a JWT token for a user"""
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow(),
        'user_id': user_id
    }
    return jwt.encode(
        payload,
        current_app.config.get('JWT_SECRET_KEY'),
        algorithm='HS256'
    )

def token_required(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # First, check the Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # If no token in header, check query parameter (useful for direct downloads)
        if not token and 'token' in request.args:
            token = request.args.get('token')
            
        # If still no token, return error
        if not token:
            return jsonify({
                'message': 'Authentication token is missing',
                'status': 401
            }), 401
            
        try:
            # Decode the token
            payload = jwt.decode(
                token, 
                current_app.config.get('JWT_SECRET_KEY'),
                algorithms=['HS256']
            )
            
            # Get the user from the database
            current_user = User.query.get(payload['user_id'])
            
            if not current_user:
                return jsonify({
                    'message': 'User not found',
                    'status': 401
                }), 401
                
            # Pass the user to the route
            return f(current_user, *args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'message': 'Authentication token has expired',
                'status': 401
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'message': 'Invalid authentication token',
                'status': 401
            }), 401
            
    return decorated

def admin_required(f):
    """Decorator for routes that require admin access"""
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({
                'message': 'Admin access required',
                'status': 403
            }), 403
        return f(current_user, *args, **kwargs)
    
    return decorated 