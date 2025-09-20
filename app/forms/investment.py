from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SelectField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class InvestmentForm(FlaskForm):
    title = StringField('Investment Title', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    investment_type = SelectField('Investment Type', choices=[
        ('equity', 'Equity Investment'),
        ('debt', 'Debt Investment'),
        ('revenue_share', 'Revenue Share'),
        ('land_lease', 'Land Lease')
    ], validators=[DataRequired()])
    amount_requested = FloatField('Amount Requested', validators=[DataRequired(), NumberRange(min=1000)])
    minimum_investment = FloatField('Minimum Investment', validators=[DataRequired(), NumberRange(min=100)])
    maximum_investment = FloatField('Maximum Investment', validators=[Optional(), NumberRange(min=100)])
    interest_rate = FloatField('Interest Rate (%)', validators=[Optional(), NumberRange(min=0, max=50)])
    expected_return = FloatField('Expected Annual Return (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    duration_months = IntegerField('Duration (Months)', validators=[Optional(), NumberRange(min=1, max=120)])
    risk_level = SelectField('Risk Level', choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk')
    ], validators=[DataRequired()])
    target_date = DateField('Fundraising Target Date', validators=[Optional()])
    submit = SubmitField('Create Investment Opportunity')

class InvestmentProposalForm(FlaskForm):
    amount = FloatField('Investment Amount', validators=[DataRequired(), NumberRange(min=100)])
    message = TextAreaField('Message to Farmer', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Proposal')
