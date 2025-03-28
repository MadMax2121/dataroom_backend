import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename):
    """Check if a file has an allowed extension"""
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv', 'zip', 'rar', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    """Save a file to disk and return its filename and path"""
    if not file or not allowed_file(file.filename):
        return None, None, None
    
    # Create a unique filename
    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    new_filename = f"{uuid.uuid4().hex}.{ext}" if ext else f"{uuid.uuid4().hex}"
    
    # Get the upload folder path
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    # Ensure the upload folder exists
    os.makedirs(upload_folder, exist_ok=True)
    
    # Create the path where the file will be saved
    file_path = os.path.join(upload_folder, new_filename)
    
    # Store the absolute path for better compatibility with send_file
    abs_path = os.path.abspath(file_path)
    
    print(f"Saving file {new_filename} to path: {abs_path}")
    
    # Save the file
    file.save(abs_path)
    
    # Generate a URL for the file
    file_url = f"/api/documents/{new_filename}/download"
    
    # Return both the absolute path that can be used directly with send_file
    return new_filename, abs_path, file_url

def delete_file(filename):
    """Delete a file from disk"""
    if not filename:
        return False
    
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    abs_path = os.path.abspath(file_path)
    
    try:
        if os.path.exists(abs_path):
            os.remove(abs_path)
            return True
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        return False
    
    return False

def get_file_type(filename):
    """Get the MIME type of a file based on its extension"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    mime_types = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'ppt': 'application/vnd.ms-powerpoint',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'txt': 'text/plain',
        'csv': 'text/csv',
        'zip': 'application/zip',
        'rar': 'application/x-rar-compressed',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif'
    }
    
    return mime_types.get(ext, 'application/octet-stream') 