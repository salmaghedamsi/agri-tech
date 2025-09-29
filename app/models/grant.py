from app import db
from datetime import datetime
import uuid

class GrantApplication(db.Model):
    __tablename__ = 'grant_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Informations de base
    grant_type = db.Column(db.String(50), nullable=False)  # equipment, seeds, infrastructure
    amount_requested = db.Column(db.Float, nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    
    # Statut et suivi
    status = db.Column(db.String(20), default='Submitted')  # Submitted, Under Review, Approved, Rejected
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    applicant = db.relationship('User', backref='grant_applications')
    
    def __repr__(self):
        return f"GrantApplication('{self.application_id}', '{self.status}')"

class ApplicationDocument(db.Model):
    __tablename__ = 'application_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('grant_applications.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))  # ID, land_proof, proposal
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relation
    application = db.relationship('GrantApplication', backref='documents')
    
    def __repr__(self):
        return f"ApplicationDocument('{self.filename}')"