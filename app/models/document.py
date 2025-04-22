from datetime import datetime
from app import db

class Document(db.Model):
    """Document model for file storage and management"""
    
    __tablename__ = "documents"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    tags = db.Column(db.String(255), nullable=True)  # Comma-separated tags
    folder_id = db.Column(db.Integer, db.ForeignKey("folders.id"), nullable=True)  # Nullable for documents not in any folder
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = db.relationship("User", back_populates="documents")
    folder = db.relationship("Folder", back_populates="documents")
    
    def to_dict(self):
        """Return a dict representation of the document"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "fileUrl": self.file_url,
            "fileType": self.file_type,
            "fileSize": self.file_size,
            "tags": self.tags.split(",") if self.tags else [],
            "folderId": self.folder_id,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
            "createdBy": self.created_by,
            "folder_id": self.folder_id  # Added explicit folder_id field
        }
    
    def __repr__(self):
        return f"<Document {self.title}>" 