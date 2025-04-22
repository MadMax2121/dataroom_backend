from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app import db
from app.models.folder import Folder
from app.models.document import Document
from app.schemas import FolderSchema, FolderUpdateSchema, DocumentSchema
from app.utils.auth import token_required, admin_required
from sqlalchemy import or_
import traceback

bp = Blueprint("folders", __name__, url_prefix="/api/folders")

# Schema instances
folder_schema = FolderSchema()
folders_schema = FolderSchema(many=True)
folder_update_schema = FolderUpdateSchema()
documents_schema = DocumentSchema(many=True)

# Helper functions
def has_folder_permission(user, folder):
    """Check if user has permission to access a folder"""
    # Admin has access to all folders
    if user.role == "admin":
        return True
    
    # Owner has access
    if folder.created_by == user.id:
        return True
    
    # For simplified permissions, only owner and admin have access
    return False

@bp.route("", methods=["GET"])
@token_required
def get_folders(current_user):
    """Get all folders for the current user"""
    # Get folders owned by current user
    if current_user.role == "admin":
        # Admins can see all folders
        folders = Folder.query.all()
    else:
        # Regular users only see their own folders
        folders = Folder.query.filter_by(created_by=current_user.id).all()
    
    return jsonify({
        "message": "Folders retrieved successfully",
        "status": 200,
        "folders": folders_schema.dump(folders)
    }), 200

@bp.route("/<int:folder_id>", methods=["GET"])
@token_required
def get_folder(current_user, folder_id):
    """Get a specific folder"""
    folder = Folder.query.get(folder_id)
    if not folder:
        return jsonify({
            "message": "Folder not found",
            "status": 404
        }), 404
        
    if not has_folder_permission(current_user, folder):
        return jsonify({
            "message": "Not authorized to access this folder",
            "status": 403
        }), 403
    
    return jsonify({
        "message": "Folder retrieved successfully",
        "status": 200,
        "folder": folder_schema.dump(folder)
    }), 200

@bp.route("", methods=["POST"])
@token_required
def create_folder(current_user):
    """Create a new folder"""
    try:
        # Validate request data
        data = folder_schema.load(request.get_json())
        
        # Create new folder
        folder = Folder(
            name=data["name"],
            type=data["type"],
            created_by=current_user.id
        )
        
        # Add to database
        db.session.add(folder)
        db.session.commit()
        
        return jsonify({
            "message": "Folder created successfully",
            "status": 201,
            "folder": folder_schema.dump(folder)
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

@bp.route("/<int:folder_id>", methods=["PUT"])
@token_required
def update_folder(current_user, folder_id):
    """Update a folder"""
    folder = Folder.query.get(folder_id)
    if not folder:
        return jsonify({
            "message": "Folder not found",
            "status": 404
        }), 404
        
    if current_user.role != "admin" and folder.created_by != current_user.id:
        return jsonify({
            "message": "Not authorized to update this folder",
            "status": 403
        }), 403
        
    try:
        # Validate request data
        data = folder_update_schema.load(request.get_json())
        
        # Update folder fields
        if "name" in data:
            folder.name = data["name"]
        if "type" in data:
            folder.type = data["type"]
            
        # Save to database
        db.session.commit()
        
        return jsonify({
            "message": "Folder updated successfully",
            "status": 200,
            "folder": folder_schema.dump(folder)
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

@bp.route("/<int:folder_id>", methods=["DELETE"])
@token_required
def delete_folder(current_user, folder_id):
    """Delete a folder"""
    folder = Folder.query.get(folder_id)
    if not folder:
        return jsonify({
            "message": "Folder not found",
            "status": 404
        }), 404
        
    if current_user.role != "admin" and folder.created_by != current_user.id:
        return jsonify({
            "message": "Not authorized to delete this folder",
            "status": 403
        }), 403
        
    try:
        # Delete folder
        db.session.delete(folder)
        db.session.commit()
        
        return jsonify({
            "message": "Folder deleted successfully",
            "status": 200,
            "data": None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": f"Error: {str(e)}",
            "status": 500
        }), 500

@bp.route("/<int:folder_id>/documents", methods=["GET"])
@token_required
def get_folder_documents(current_user, folder_id):
    """Get all documents in a folder"""
    # Check if folder exists
    folder = Folder.query.get(folder_id)
    if not folder:
        return jsonify({
            "message": "Folder not found",
            "status": 404
        }), 404
        
    # Check if the user owns the folder or is an admin
    if current_user.role != "admin" and folder.created_by != current_user.id:
        return jsonify({
            "message": "Not authorized to access this folder",
            "status": 403
        }), 403
    
    # Get documents directly from folder relationship
    documents = folder.documents
    
    return jsonify({
        "message": "Documents retrieved successfully",
        "status": 200,
        "data": {
            "documents": documents_schema.dump(documents),
            "total": len(documents)
        }
    }), 200

@bp.route("/<int:folder_id>/documents", methods=["POST"])
@token_required
def add_document_to_folder(current_user, folder_id):
    """Add a document to a folder"""
    folder = Folder.query.get(folder_id)
    if not folder:
        return jsonify({
            "message": "Folder not found",
            "status": 404
        }), 404
    
    # Check if the user owns the folder or is an admin
    if current_user.role != "admin" and folder.created_by != current_user.id:
        return jsonify({
            "message": "Not authorized to modify this folder",
            "status": 403
        }), 403
    
    # Get document ID from request
    data = request.get_json()
    if not data or "documentId" not in data:
        return jsonify({
            "message": "Document ID is required",
            "status": 400
        }), 400
    
    document_id = data["documentId"]
    document = Document.query.get(document_id)
    if not document:
        return jsonify({
            "message": "Document not found",
            "status": 404
        }), 404
    
    # Check if document already in this folder using the new folder_id field
    if document.folder_id == folder_id:
        return jsonify({
            "message": "Document already in this folder",
            "status": 400
        }), 400
    
    try:
        # Set document's folder_id
        document.folder_id = folder_id
        db.session.commit()
        
        return jsonify({
            "message": "Document added to folder successfully",
            "status": 200,
            "data": {
                "folderId": folder_id,
                "documentId": document_id
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "message": f"Error: {str(e)}",
            "status": 500
        }), 500

@bp.route("/<int:folder_id>/documents/<int:document_id>", methods=["DELETE"])
@token_required
def remove_document_from_folder(current_user, folder_id, document_id):
    """Remove a document from a folder"""
    folder = Folder.query.get(folder_id)
    if not folder:
        return jsonify({
            "message": "Folder not found",
            "status": 404
        }), 404
    
    # Check if the user owns the folder or is an admin
    if current_user.role != "admin" and folder.created_by != current_user.id:
        return jsonify({
            "message": "Not authorized to modify this folder",
            "status": 403
        }), 403
    
    # Check if document exists and is in this folder
    document = Document.query.get(document_id)
    if not document or document.folder_id != folder_id:
        return jsonify({
            "message": "Document not found in this folder",
            "status": 404
        }), 404
    
    try:
        # Remove document from folder by setting folder_id to None
        document.folder_id = None
        db.session.commit()
        
        return jsonify({
            "message": "Document removed from folder successfully",
            "status": 200,
            "data": None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": f"Error: {str(e)}",
            "status": 500
        }), 500 