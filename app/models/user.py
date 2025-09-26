from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    user_type = db.Column(db.Enum('farmer', 'investor', 'expert', 'admin'), nullable=False, default='farmer')
    profile_image = db.Column(db.String(255))
    bio = db.Column(db.Text)
    
    # Farmer-specific fields
    farm_name = db.Column(db.String(100))
    farm_location = db.Column(db.String(200))
    farm_size = db.Column(db.Float)  # in acres
    farm_type = db.Column(db.String(50))  # organic, conventional, etc.
    years_experience = db.Column(db.Integer)
    farm_description = db.Column(db.Text)
    certifications = db.Column(db.Text)  # JSON string of certifications
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='seller', lazy='dynamic')
    courses_enrolled = db.relationship('CourseEnrollment', backref='user', lazy='dynamic')
    courses_created = db.relationship('Course', backref='instructor', lazy='dynamic')
    land_listings = db.relationship('Land', backref='owner', lazy='dynamic')
    investments = db.relationship('Investment', backref='investor', lazy='dynamic')
    forum_posts = db.relationship('ForumPost', backref='author', lazy='dynamic')
    forum_comments = db.relationship('ForumComment', backref='author', lazy='dynamic')
    mentoring_sessions_as_mentor = db.relationship('MentoringSession', foreign_keys='MentoringSession.mentor_id', backref='mentor', lazy='dynamic')
    mentoring_sessions_as_mentee = db.relationship('MentoringSession', foreign_keys='MentoringSession.mentee_id', backref='mentee', lazy='dynamic')
    mentoring_requests = db.relationship('MentoringRequest', backref='mentee', lazy='dynamic')
    chat_sessions = db.relationship('ChatSession', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Return user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def is_farmer(self):
        """Check if user is a farmer"""
        return self.user_type == 'farmer'
    
    def is_investor(self):
        """Check if user is an investor"""
        return self.user_type == 'investor'
    
    def is_expert(self):
        """Check if user is an expert"""
        return self.user_type == 'expert'
    
    def is_admin(self):
        """Check if user is an admin"""
        return self.user_type == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'
