from datetime import datetime
from app import db

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    thumbnail_url = db.Column(db.String(255))
    price = db.Column(db.Float, default=0.0)  # 0 for free courses
    duration_hours = db.Column(db.Float, default=0.0)
    difficulty_level = db.Column(db.Enum('beginner', 'intermediate', 'advanced'), default='beginner')
    language = db.Column(db.String(10), default='en')  # en, ar, fr
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    modules = db.relationship('CourseModule', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    enrollments = db.relationship('CourseEnrollment', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_total_students(self):
        """Get total number of enrolled students"""
        return self.enrollments.count()
    
    def get_average_rating(self):
        """Calculate average rating from enrollments"""
        enrollments = self.enrollments.filter(CourseEnrollment.rating.isnot(None)).all()
        if not enrollments:
            return 0
        return sum(enrollment.rating for enrollment in enrollments) / len(enrollments)
    
    def __repr__(self):
        return f'<Course {self.title}>'

class CourseModule(db.Model):
    __tablename__ = 'course_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)  # Video URL, text content, etc.
    content_type = db.Column(db.Enum('video', 'text', 'quiz', 'assignment'), default='video')
    duration_minutes = db.Column(db.Integer, default=0)
    order_index = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    def __repr__(self):
        return f'<CourseModule {self.title}>'

class CourseEnrollment(db.Model):
    __tablename__ = 'course_enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    rating = db.Column(db.Integer)  # 1-5 stars
    review = db.Column(db.Text)
    is_completed = db.Column(db.Boolean, default=False)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    # Relationships
    progress = db.relationship('CourseProgress', backref='enrollment', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_progress_percentage(self):
        """Calculate completion percentage"""
        total_modules = self.course.modules.count()
        if total_modules == 0:
            return 0
        completed_modules = self.progress.filter(CourseProgress.is_completed == True).count()
        return (completed_modules / total_modules) * 100
    
    def __repr__(self):
        return f'<CourseEnrollment {self.user.username} - {self.course.title}>'

class CourseProgress(db.Model):
    __tablename__ = 'course_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    time_spent_minutes = db.Column(db.Integer, default=0)
    
    # Foreign keys
    enrollment_id = db.Column(db.Integer, db.ForeignKey('course_enrollments.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('course_modules.id'), nullable=False)
    
    def __repr__(self):
        return f'<CourseProgress {self.enrollment.user.username} - {self.module.title}>'
