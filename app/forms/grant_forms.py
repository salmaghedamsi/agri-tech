from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import FloatField, TextAreaField, SelectField
from wtforms.validators import DataRequired, NumberRange, Length

class GrantApplicationForm(FlaskForm):
    grant_type = SelectField('Grant Type', 
        choices=[
            ('', '👉 Choose a grant type'),
            ('equipment', '🛠️ Agricultural Equipment'),
            ('seeds', '🌱 Seeds and Plants'),
            ('infrastructure', '🏗️ Infrastructure'),
            ('training', '📚 Training'),
            ('other', '❔ Other')
        ], 
        validators=[DataRequired(message="🔍 Please choose a grant type")]
    )
    
    amount_requested = FloatField('Amount Requested (€)', 
        validators=[
            DataRequired(message="💰 Please enter an amount"),
            NumberRange(min=100, max=100000, message="💸 Amount must be between €100 and €100,000")
        ],
        render_kw={"placeholder": "5000"}
    )
    
    purpose = TextAreaField('Purpose of Grant', 
        validators=[
            DataRequired(message="📝 Please describe your project purpose"),
            Length(min=50, max=1000, message="📄 Description must be between 50 and 1000 characters (currently: %(length)d)")
        ],
        render_kw={
            "placeholder": "Describe in detail how this grant will help your farm...",
            "rows": 6
        }
    )
    
    documents = FileField('Supporting Documents', 
        validators=[
            FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'], 
                       '📎 Accepted formats: PDF, Word, JPG, PNG (max 10MB)')
        ],
        render_kw={"class": "form-control"}
    )