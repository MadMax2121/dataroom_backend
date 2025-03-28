from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app import db
from app.models.user import User
from app.schemas import UserSchema, UserUpdateSchema, LoginSchema
from app.utils.auth import token_required, admin_required, generate_token

bp = Blueprint("users", __name__, url_prefix="/api/users")

# Schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_update_schema = UserUpdateSchema()
login_schema = LoginSchema()

@bp.route("/register", methods=["POST"])
def register():
    """Register a new user"""
    try:
        # Validate request data
        data = user_schema.load(request.get_json())
        
        # Check if user with this email already exists
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({
                "message": "User with this email already exists",
                "status": 400
            }), 400
            
        # Check if user with this username already exists
        if User.query.filter_by(username=data["username"]).first():
            return jsonify({
                "message": "User with this username already exists",
                "status": 400
            }), 400
            
        # Create new user
        user = User(
            username=data["username"],
            email=data["email"],
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            role="user"
        )
        user.password = data["password"]
        
        # Save to database
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = generate_token(user.id)
        
        return jsonify({
            "message": "User registered successfully",
            "status": 201,
            "token": token,
            "user": user_schema.dump(user)
        }), 201
        
    except ValidationError as e:
        return jsonify({
            "message": "Validation error",
            "errors": e.messages,
            "status": 400
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": f"Error: {str(e)}",
            "status": 500
        }), 500

@bp.route("/login", methods=["POST"])
def login():
    """Login a user"""
    try:
        # Validate request data
        data = login_schema.load(request.get_json())
        
        # Check if user exists and password is correct
        user = User.query.filter_by(email=data["email"]).first()
        if not user or not user.verify_password(data["password"]):
            return jsonify({
                "message": "Invalid email or password",
                "status": 401
            }), 401
            
        # Generate token
        token = generate_token(user.id)
        
        return jsonify({
            "message": "Login successful",
            "status": 200,
            "token": token,
            "user": user_schema.dump(user)
        }), 200
        
    except ValidationError as e:
        return jsonify({
            "message": "Validation error",
            "errors": e.messages,
            "status": 400
        }), 400
    except Exception as e:
        return jsonify({
            "message": f"Error: {str(e)}",
            "status": 500
        }), 500

@bp.route("/me", methods=["GET"])
@token_required
def get_current_user(current_user):
    """Get current user profile"""
    return jsonify({
        "message": "User profile retrieved successfully",
        "status": 200,
        "user": user_schema.dump(current_user)
    }), 200

@bp.route("/<int:user_id>", methods=["GET"])
@token_required
def get_user(current_user, user_id):
    """Get a user by ID"""
    # Check if admin or the user is requesting their own profile
    if current_user.role != "admin" and current_user.id != user_id:
        return jsonify({
            "message": "Not authorized to access this user profile",
            "status": 403
        }), 403
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            "message": "User not found",
            "status": 404
        }), 404
        
    return jsonify({
        "message": "User profile retrieved successfully",
        "status": 200,
        "user": user_schema.dump(user)
    }), 200

@bp.route("/<int:user_id>", methods=["PUT"])
@token_required
def update_user(current_user, user_id):
    """Update a user profile"""
    # Check if admin or the user is updating their own profile
    if current_user.role != "admin" and current_user.id != user_id:
        return jsonify({
            "message": "Not authorized to update this user profile",
            "status": 403
        }), 403
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            "message": "User not found",
            "status": 404
        }), 404
        
    try:
        # Validate request data
        data = user_update_schema.load(request.get_json())
        
        # Check if email already exists for another user
        if "email" in data and data["email"] != user.email and User.query.filter_by(email=data["email"]).first():
            return jsonify({
                "message": "User with this email already exists",
                "status": 400
            }), 400
            
        # Check if username already exists for another user
        if "username" in data and data["username"] != user.username and User.query.filter_by(username=data["username"]).first():
            return jsonify({
                "message": "User with this username already exists",
                "status": 400
            }), 400
            
        # Update user fields
        if "username" in data:
            user.username = data["username"]
        if "email" in data:
            user.email = data["email"]
        if "password" in data:
            user.password = data["password"]
        if "first_name" in data:
            user.first_name = data["first_name"]
        if "last_name" in data:
            user.last_name = data["last_name"]
            
        # Save to database
        db.session.commit()
        
        return jsonify({
            "message": "User profile updated successfully",
            "status": 200,
            "user": user_schema.dump(user)
        }), 200
        
    except ValidationError as e:
        return jsonify({
            "message": "Validation error",
            "errors": e.messages,
            "status": 400
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": f"Error: {str(e)}",
            "status": 500
        }), 500

@bp.route("", methods=["GET"])
@admin_required
def get_all_users(current_user):
    """Get all users (admin only)"""
    # Parse pagination parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("pageSize", 10, type=int)
    
    # Get paginated users
    pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    
    return jsonify({
        "message": "Users retrieved successfully",
        "status": 200,
        "data": {
            "items": users_schema.dump(users),
            "total": pagination.total,
            "page": page,
            "pageSize": per_page,
            "totalPages": pagination.pages
        }
    }), 200

@bp.route("/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(current_user, user_id):
    """Delete a user (admin only)"""
    # Prevent admin from deleting themselves
    if current_user.id == user_id:
        return jsonify({
            "message": "Cannot delete your own account",
            "status": 400
        }), 400
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            "message": "User not found",
            "status": 404
        }), 404
        
    try:
        # Delete user from database
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            "message": "User deleted successfully",
            "status": 200,
            "data": None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": f"Error: {str(e)}",
            "status": 500
        }), 500 