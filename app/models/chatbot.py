from datetime import datetime
from app import db

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    language = db.Column(db.Enum('en', 'ar', 'tn'), default='en')  # English, Arabic, Tunisian
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Nullable for anonymous users
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_message_count(self):
        """Get total number of messages in this session"""
        return self.messages.count()
    
    def get_latest_message(self):
        """Get the latest message in this session"""
        return self.messages.order_by(ChatMessage.timestamp.desc()).first()
    
    def __repr__(self):
        return f'<ChatSession {self.session_id}>'

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.Enum('user', 'bot', 'system'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_helpful = db.Column(db.Boolean)  # User feedback on bot responses
    response_time_ms = db.Column(db.Integer)  # Bot response time in milliseconds
    
    # Foreign keys
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    
    def get_time_ago(self):
        """Get human-readable time ago string"""
        now = datetime.utcnow()
        diff = now - self.timestamp
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    
    def __repr__(self):
        return f'<ChatMessage {self.id} - {self.message_type}>'
