import os
from flask import Blueprint, request, jsonify, current_app, send_file
from marshmallow import ValidationError
from werkzeug.utils import secure_filename
from app import db
from app.models.document import Document, DocumentTag
from app.schemas import DocumentSchema, DocumentUpdateSchema
from app.utils.auth import token_required, admin_required
from app.utils.file_handler import save_file, delete_file, get_file_type

bp = Blueprint("documents", __name__, url_prefix="/api/documents")

# Schemas
document_schema = DocumentSchema()
documents_schema = DocumentSchema(many=True)
document_update_schema = DocumentUpdateSchema()

@bp.route("", methods=["GET"])
@token_required
def get_documents(current_user):
    """Get all documents with pagination and filtering"""
    # Parse pagination parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("pageSize", 10, type=int)
    sort_by = request.args.get("sortBy", "created_at")
    sort_order = request.args.get("sortOrder", "desc")
    
    # Build query
    query = Document.query
    
    # Apply filters if provided
    if request.args.get("search"):
        search_term = f"%{request.args.get('search')}%"
        query = query.filter(Document.title.ilike(search_term) | Document.description.ilike(search_term))
    
    # Apply sorting
    if sort_order == "desc":
        query = query.order_by(getattr(Document, sort_by).desc())
    else:
        query = query.order_by(getattr(Document, sort_by))
    
    # Get paginated documents
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    documents = pagination.items
    
    return jsonify({
        "message": "Documents retrieved successfully",
        "status": 200,
        "items": documents_schema.dump(documents),
        "total": pagination.total,
        "page": page,
        "pageSize": per_page,
        "totalPages": pagination.pages
    }), 200

@bp.route("/<int:document_id>", methods=["GET"])
@token_required
def get_document(current_user, document_id):
    """Get a document by ID"""
    document = Document.query.get(document_id)
    if not document:
        return jsonify({
            "message": "Document not found",
            "status": 404
        }), 404
    
    return jsonify({
        "message": "Document retrieved successfully",
        "status": 200,
        "document": document_schema.dump(document)
    }), 200

@bp.route("", methods=["POST"])
@token_required
def create_document(current_user):
    """Create a new document"""
    try:
        # Check if file is present in the request
        if "file" not in request.files:
            return jsonify({
                "message": "No file part in the request",
                "status": 400
            }), 400
            
        file = request.files["file"]
        if file.filename == "":
            return jsonify({
                "message": "No file selected",
                "status": 400
            }), 400
            
        # Get form data
        title = request.form.get("title")
        description = request.form.get("description", "")
        tags = request.form.getlist("tags[]") if "tags[]" in request.form else []
        
        # Validate required fields
        if not title:
            return jsonify({
                "message": "Title is required",
                "status": 400
            }), 400
            
        # Save the file and get the file info
        filename, file_path, file_url = save_file(file)
        if not filename:
            return jsonify({
                "message": "Invalid file or file type not allowed",
                "status": 400
            }), 400
            
        # Create new document
        document = Document(
            title=title,
            description=description,
            file_path=file_path,
            file_url=file_url,
            file_type=get_file_type(file.filename),
            file_size=os.path.getsize(file_path),
            created_by=current_user.id
        )
        
        # Add to database
        db.session.add(document)
        db.session.flush()  # Get document ID
        
        # Add tags
        for tag in tags:
            doc_tag = DocumentTag(document_id=document.id, name=tag)
            db.session.add(doc_tag)
            
        db.session.commit()
        
        return jsonify({
            "message": "Document created successfully",
            "status": 201,
            "document": document_schema.dump(document)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": f"Error: {str(e)}",
            "status": 500
        }), 500

@bp.route("/<int:document_id>", methods=["PUT"])
@token_required
def update_document(current_user, document_id):
    """Update a document"""
    document = Document.query.get(document_id)
    if not document:
        return jsonify({
            "message": "Document not found",
            "status": 404
        }), 404
        
    # Check if the user owns the document or is an admin
    if current_user.role != "admin" and document.created_by != current_user.id:
        return jsonify({
            "message": "Not authorized to update this document",
            "status": 403
        }), 403
        
    try:
        # Validate request data
        data = document_update_schema.load(request.get_json())
        
        # Update document fields
        if "title" in data:
            document.title = data["title"]
        if "description" in data:
            document.description = data["description"]
            
        # Update tags if provided
        if "tags" in data:
            # Remove existing tags
            DocumentTag.query.filter_by(document_id=document.id).delete()
            
            # Add new tags
            for tag in data["tags"]:
                doc_tag = DocumentTag(document_id=document.id, name=tag)
                db.session.add(doc_tag)
                
        # Save to database
        db.session.commit()
        
        return jsonify({
            "message": "Document updated successfully",
            "status": 200,
            "document": document_schema.dump(document)
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

@bp.route("/<int:document_id>", methods=["DELETE"])
@token_required
def delete_document(current_user, document_id):
    """Delete a document"""
    document = Document.query.get(document_id)
    if not document:
        return jsonify({
            "message": "Document not found",
            "status": 404
        }), 404
        
    # Check if the user owns the document or is an admin
    if current_user.role != "admin" and document.created_by != current_user.id:
        return jsonify({
            "message": "Not authorized to delete this document",
            "status": 403
        }), 403
        
    try:
        # Delete the file from disk
        file_name = os.path.basename(document.file_path)
        delete_file(file_name)
        
        # Delete document from database
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({
            "message": "Document deleted successfully",
            "status": 200,
            "data": None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": f"Error: {str(e)}",
            "status": 500
        }), 500

@bp.route("/<int:document_id>/download", methods=["GET"])
@token_required
def download_document(current_user, document_id):
    """Download a document file"""
    try:
        # Add CORS headers for the download
        response_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
        
        document = Document.query.get(document_id)
        if not document:
            return jsonify({
                "message": "Document not found",
                "status": 404
            }), 404, response_headers
            
        # Print document details for debugging
        print(f"Document found: id={document.id}, title={document.title}")
        print(f"Document properties: file_path={document.file_path}, file_type={document.file_type}, file_size={document.file_size}")
        
        # Check if file_path is None or empty
        if not document.file_path:
            return jsonify({
                "message": "Document has no file path",
                "status": 400
            }), 400, response_headers
        
        # Get the absolute path by resolving relative to app root
        # This should fix the issue when paths are stored as relative but need to be absolute
        if not os.path.isabs(document.file_path):
            # If it's a relative path, make it absolute relative to the app root
            abs_file_path = os.path.join(current_app.root_path, '..', document.file_path)
            abs_file_path = os.path.normpath(abs_file_path)
        else:
            # If it's already absolute, use it directly
            abs_file_path = document.file_path
            
        print(f"Original file path: {document.file_path}")
        print(f"Resolved absolute path: {abs_file_path}")
        
        # Check if file exists at path
        if not os.path.exists(abs_file_path):
            print(f"File not found on disk: {abs_file_path}")
            print(f"Current working directory: {os.getcwd()}")
            
            # Try to list uploads directory
            upload_dir = os.path.dirname(abs_file_path)
            try:
                print(f"Listing contents of {upload_dir}:")
                for file in os.listdir(upload_dir):
                    print(f"  - {file}")
            except Exception as list_err:
                print(f"Error listing directory: {str(list_err)}")
                
            return jsonify({
                "message": f"File not found on server: {abs_file_path}",
                "status": 404
            }), 404, response_headers
            
        print(f"Attempting to send file: {abs_file_path}")
        print(f"File exists: {os.path.exists(abs_file_path)}")
        print(f"File size: {os.path.getsize(abs_file_path)}")
        print(f"File mimetype: {document.file_type}")
        
        # Use explicit attachment_filename to avoid compatibility issues
        try:
            response = send_file(
                abs_file_path, 
                mimetype=document.file_type,
                download_name=secure_filename(document.title),
                as_attachment=True
            )
            
            # Add CORS headers to the response
            for header, value in response_headers.items():
                response.headers[header] = value
                
            return response
            
        except Exception as send_err:
            print(f"Error sending file: {str(send_err)}")
            return jsonify({
                "message": f"Error sending file: {str(send_err)}",
                "status": 500
            }), 500, response_headers
        
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Error during download: {str(e)}")
        print(f"Traceback: {traceback_str}")
        return jsonify({
            "message": f"Error: {str(e)}",
            "status": 500
        }), 500

@bp.route("/search", methods=["GET"])
@token_required
def search_documents(current_user):
    """Search documents by title, description or tags"""
    # Get search query
    search_term = request.args.get("q", "")
    if not search_term:
        return jsonify({
            "message": "Search query is required",
            "status": 400
        }), 400
        
    # Parse pagination parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("pageSize", 10, type=int)
    
    # Build the search query
    search_pattern = f"%{search_term}%"
    query = Document.query.filter(
        Document.title.ilike(search_pattern) | 
        Document.description.ilike(search_pattern)
    )
    
    # Get documents that match by tags
    tag_document_ids = db.session.query(DocumentTag.document_id).filter(
        DocumentTag.name.ilike(search_pattern)
    ).all()
    tag_document_ids = [id[0] for id in tag_document_ids]
    
    if tag_document_ids:
        query = query.union(Document.query.filter(Document.id.in_(tag_document_ids)))
    
    # Get paginated documents
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    documents = pagination.items
    
    return jsonify({
        "message": "Search results",
        "status": 200,
        "data": {
            "items": documents_schema.dump(documents),
            "total": pagination.total,
            "page": page,
            "pageSize": per_page,
            "totalPages": pagination.pages
        }
    }), 200 