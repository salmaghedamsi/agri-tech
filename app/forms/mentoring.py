from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class MentoringRequestForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    preferred_time = DateTimeField('Preferred Time', validators=[Optional()])
    duration_minutes = SelectField('Duration', choices=[
        (30, '30 minutes'),
        (60, '1 hour'),
        (90, '1.5 hours'),
        (120, '2 hours')
    ], coerce=int, validators=[DataRequired()])
    mentor_id = SelectField('Select Mentor', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Send Request')

class MentoringSessionForm(FlaskForm):
    title = StringField('Session Title', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    scheduled_time = DateTimeField('Scheduled Time', validators=[DataRequired()])
    duration_minutes = SelectField('Duration', choices=[
        (30, '30 minutes'),
        (60, '1 hour'),
        (90, '1.5 hours'),
        (120, '2 hours')
    ], coerce=int, validators=[DataRequired()])
    meeting_link = StringField('Meeting Link', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Schedule Session')
