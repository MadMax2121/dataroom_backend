from datetime import datetime
from app import db

class Folder(db.Model):
    """Folder model for organizing documents"""
    
    __tablename__ = "folders"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False, default="private")  # 'private' or 'team'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = db.relationship("User", back_populates="folders")
    documents = db.relationship("Document", back_populates="folder", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Return a dict representation of the folder"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
            "createdBy": self.created_by,
            "documentCount": len(self.documents) if self.documents else 0
        }
    
    def __repr__(self):
        return f"<Folder {self.name}>" 