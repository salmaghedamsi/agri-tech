from datetime import datetime
from app import db

class ForumCategory(db.Model):
    __tablename__ = 'forum_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # Font Awesome icon class
    color = db.Column(db.String(7))  # Hex color code
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    posts = db.relationship('ForumPost', backref='category', lazy='dynamic')
    
    def get_post_count(self):
        """Get total number of posts in this category"""
        return self.posts.count()
    
    def get_latest_post(self):
        """Get the latest post in this category"""
        return self.posts.order_by(ForumPost.created_at.desc()).first()
    
    def __repr__(self):
        return f'<ForumCategory {self.name}>'

class ForumPost(db.Model):
    __tablename__ = 'forum_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_pinned = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('forum_categories.id'), nullable=False)
    
    # Relationships
    comments = db.relationship('ForumComment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_comment_count(self):
        """Get total number of comments"""
        return self.comments.count()
    
    def get_latest_comment(self):
        """Get the latest comment"""
        return self.comments.order_by(ForumComment.created_at.desc()).first()
    
    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        db.session.commit()
    
    def __repr__(self):
        return f'<ForumPost {self.title}>'

class ForumComment(db.Model):
    __tablename__ = 'forum_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    like_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('forum_comments.id'))  # For nested comments
    
    # Relationships
    replies = db.relationship('ForumComment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    def get_reply_count(self):
        """Get total number of replies"""
        return self.replies.count()
    
    def __repr__(self):
        return f'<ForumComment {self.id}>'
