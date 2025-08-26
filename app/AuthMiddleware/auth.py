from functools import wraps
from flask import request, jsonify
import jwt


# def subscription_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         is_valid, message = validate_subscription()
#         if not is_valid:
#             return jsonify({"error": message}), 403
#         return f(*args, **kwargs)
#     return decorated_function

# def admin_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         token = request.headers.get('Authorization')
#         if not token:
#             return jsonify({"error": "Authorization token required"}), 401
        
#         try:
#             if token.startswith('Bearer '):
#                 token = token[7:]
#             payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
#             admin_id = payload.get('admin_id')
#             admin = AdminUser.query.get(admin_id)
            
#             if not admin:
#                 return jsonify({"error": "Invalid admin"}), 401
                
#             # Store admin in request context for logging
#             request.admin_user = admin
#             return f(*args, **kwargs)
            
#         except jwt.ExpiredSignatureError:
#             return jsonify({"error": "Token expired"}), 401
#         except jwt.InvalidTokenError:
#             return jsonify({"error": "Invalid token"}), 401
#     return decorated_function