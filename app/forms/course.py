from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FloatField, IntegerField, BooleanField, SelectField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, URL

class CourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[NumberRange(min=0)])
    duration_hours = FloatField('Duration (Hours)', validators=[NumberRange(min=0)])
    difficulty_level = SelectField('Difficulty Level', choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], validators=[DataRequired()])
    language = SelectField('Language', choices=[
        ('en', 'English'),
        ('ar', 'Arabic'),
        ('fr', 'French')
    ], validators=[DataRequired()])
    thumbnail = FileField('Course Thumbnail', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    document = FileField('Course Document', validators=[FileAllowed(['pdf', 'doc', 'docx', 'txt'])])
    tutorial_video_url = URLField('Tutorial Video URL', validators=[Optional(), URL()])
    is_published = BooleanField('Publish Course')
    submit = SubmitField('Create Course')

class CourseModuleForm(FlaskForm):
    title = StringField('Module Title', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    content = TextAreaField('Content', validators=[DataRequired()])
    content_type = SelectField('Content Type', choices=[
        ('video', 'Video'),
        ('text', 'Text'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('document', 'Document'),
        ('video_plus_doc', 'Video with Document')
    ], validators=[DataRequired()])
    video_url = URLField('Video URL', validators=[Optional(), URL()])
    document = FileField('Module Document', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt'], 'Documents only!')
    ])
    duration_minutes = IntegerField('Duration (Minutes)', validators=[NumberRange(min=0)])
    order_index = IntegerField('Order', validators=[NumberRange(min=0)])
    is_required = BooleanField('Required to Complete', default=True)
    is_published = BooleanField('Publish Module')
    submit = SubmitField('Add Module')
