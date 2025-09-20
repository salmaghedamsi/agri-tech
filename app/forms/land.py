from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FloatField, IntegerField, BooleanField, SelectField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class LandForm(FlaskForm):
    title = StringField('Property Title', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), Length(max=200)])
    latitude = FloatField('Latitude', validators=[Optional(), NumberRange(min=-90, max=90)])
    longitude = FloatField('Longitude', validators=[Optional(), NumberRange(min=-180, max=180)])
    area_acres = FloatField('Area (Acres)', validators=[DataRequired(), NumberRange(min=0.1)])
    price_per_acre = FloatField('Price per Acre', validators=[DataRequired(), NumberRange(min=0)])
    land_type = SelectField('Land Type', choices=[
        ('agricultural', 'Agricultural'),
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('mixed', 'Mixed Use')
    ], validators=[DataRequired()])
    soil_type = StringField('Soil Type', validators=[Optional(), Length(max=100)])
    water_source = StringField('Water Source', validators=[Optional(), Length(max=100)])
    infrastructure = TextAreaField('Infrastructure Details', validators=[Optional()])
    listing_type = SelectField('Listing Type', choices=[
        ('sale', 'For Sale'),
        ('lease', 'For Lease'),
        ('both', 'Both Sale and Lease')
    ], validators=[DataRequired()])
    images = FileField('Property Images', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    submit = SubmitField('List Property')

class LandInvestmentForm(FlaskForm):
    investment_amount = FloatField('Investment Amount', validators=[DataRequired(), NumberRange(min=100)])
    ownership_percentage = FloatField('Desired Ownership %', validators=[DataRequired(), NumberRange(min=0.1, max=100)])
    submit = SubmitField('Submit Investment Proposal')

class LandLeaseForm(FlaskForm):
    monthly_rent = FloatField('Monthly Rent', validators=[DataRequired(), NumberRange(min=0)])
    lease_duration_months = IntegerField('Lease Duration (Months)', validators=[DataRequired(), NumberRange(min=1, max=120)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    terms_conditions = TextAreaField('Terms and Conditions', validators=[Optional()])
    submit = SubmitField('Submit Lease Proposal')
