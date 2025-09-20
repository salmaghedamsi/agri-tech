from datetime import datetime
from app import db

class Mentor(db.Model):
    __tablename__ = 'mentors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    specialization = db.Column(db.String(200), nullable=False)
    experience_years = db.Column(db.Integer, nullable=False)
    hourly_rate = db.Column(db.Float, default=0.0)  # 0 for free mentoring
    bio = db.Column(db.Text)
    languages = db.Column(db.String(100))  # Comma-separated languages
    availability_schedule = db.Column(db.Text)  # JSON string for availability
    is_available = db.Column(db.Boolean, default=True)
    rating = db.Column(db.Float, default=0.0)
    total_sessions = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sessions = db.relationship('MentoringSession', backref='mentor_profile', lazy='dynamic')
    requests = db.relationship('MentoringRequest', backref='mentor_profile', lazy='dynamic')
    
    def get_user(self):
        """Get the user associated with this mentor profile"""
        from app.models.user import User
        return User.query.get(self.user_id)
    
    def get_average_rating(self):
        """Calculate average rating from completed sessions"""
        completed_sessions = self.sessions.filter(MentoringSession.status == 'completed').all()
        if not completed_sessions:
            return 0.0
        ratings = [session.rating for session in completed_sessions if session.rating]
        if not ratings:
            return 0.0
        return sum(ratings) / len(ratings)
    
    def __repr__(self):
        return f'<Mentor {self.get_user().username if self.get_user() else "Unknown"}>'

class MentoringRequest(db.Model):
    __tablename__ = 'mentoring_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    preferred_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer, default=60)
    status = db.Column(db.Enum('pending', 'accepted', 'rejected', 'cancelled'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    mentee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentors.id'), nullable=False)
    
    # Relationships
    sessions = db.relationship('MentoringSession', backref='request', lazy='dynamic')
    
    def __repr__(self):
        return f'<MentoringRequest {self.subject}>'

class MentoringSession(db.Model):
    __tablename__ = 'mentoring_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    meeting_link = db.Column(db.String(500))  # Zoom, Google Meet, etc.
    status = db.Column(db.Enum('scheduled', 'in_progress', 'completed', 'cancelled', 'no_show'), default='scheduled')
    notes = db.Column(db.Text)  # Session notes
    rating = db.Column(db.Integer)  # 1-5 stars
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    mentor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mentee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mentor_profile_id = db.Column(db.Integer, db.ForeignKey('mentors.id'), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('mentoring_requests.id'))
    
    def get_status_color(self):
        """Get color based on session status"""
        color_map = {
            'scheduled': 'info',
            'in_progress': 'warning',
            'completed': 'success',
            'cancelled': 'danger',
            'no_show': 'secondary'
        }
        return color_map.get(self.status, 'info')
    
    def get_status_icon(self):
        """Get icon based on session status"""
        icon_map = {
            'scheduled': 'calendar',
            'in_progress': 'play-circle',
            'completed': 'check-circle',
            'cancelled': 'times-circle',
            'no_show': 'exclamation-circle'
        }
        return icon_map.get(self.status, 'question-circle')
    
    def __repr__(self):
        return f'<MentoringSession {self.title}>'
