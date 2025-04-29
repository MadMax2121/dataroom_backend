from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import ARRAY

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
    tags = db.Column(ARRAY(db.String(50)), nullable=True, default=[])  # Make sure nullable is True and store tags as an array
    folder_id = db.Column(db.Integer, db.ForeignKey("folders.id"), nullable=True)  # The folder this document belongs to
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = db.relationship("User", back_populates="documents")
    folder = db.relationship("Folder", backref="documents")  # Document knows which folder it belongs to
    
    def to_dict(self):
        """Return a dict representation of the document"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "fileUrl": self.file_url,
            "fileType": self.file_type,
            "fileSize": self.file_size,
            "tags": self.tags or [],  # Return the tags directly, ensuring not None
            "folder_id": self.folder_id,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
            "createdBy": self.created_by
        }
    
    def __repr__(self):
        return f"<Document {self.title}>"

# The DocumentTag model is no longer needed 