from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, FloatField, IntegerField, BooleanField, SelectField, SubmitField, DateField, MultipleFileField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError
from datetime import date

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=1000)])
    price = FloatField('Price per Unit ($)', validators=[DataRequired(), NumberRange(min=0.01, message="Price must be greater than 0")])
    quantity = IntegerField('Available Quantity', validators=[DataRequired(), NumberRange(min=0)])
    unit = SelectField('Unit', choices=[
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('lb', 'Pound'),
        ('piece', 'Piece'),
        ('liter', 'Liter'),
        ('gallon', 'Gallon'),
        ('box', 'Box'),
        ('bag', 'Bag'),
        ('dozen', 'Dozen'),
        ('bunch', 'Bunch')
    ], validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    
    # Image uploads
    image = FileField('Product Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    main_image = FileField('Main Product Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    additional_images = MultipleFileField('Additional Images (Optional)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    
    # Product details
    is_organic = BooleanField('Organic Product')
    is_active = BooleanField('Product Active', default=True)
    harvest_date = DateField('Harvest Date (Optional)', validators=[Optional()])
    expiry_date = DateField('Expiry Date (Optional)', validators=[Optional()])
    min_order_quantity = IntegerField('Minimum Order Quantity', validators=[Optional(), NumberRange(min=1)], default=1)
    
    # Delivery options
    delivery_available = BooleanField('Delivery Available')
    delivery_radius = IntegerField('Delivery Radius (km)', validators=[Optional(), NumberRange(min=1, max=500)])
    
    submit = SubmitField('Save Product')
    
    def validate_expiry_date(self, field):
        if field.data and self.harvest_date.data and field.data <= self.harvest_date.data:
            raise ValidationError('Expiry date must be after harvest date.')

class FarmerProfileForm(FlaskForm):
    # Basic info
    farm_name = StringField('Farm Name', validators=[DataRequired(), Length(min=2, max=100)])
    farm_location = StringField('Farm Location', validators=[DataRequired(), Length(min=5, max=200)])
    farm_size = FloatField('Farm Size (acres)', validators=[DataRequired(), NumberRange(min=0.1, max=10000)])
    farm_type = SelectField('Farm Type', choices=[
        ('organic', 'Organic'),
        ('conventional', 'Conventional'),
        ('biodynamic', 'Biodynamic'),
        ('permaculture', 'Permaculture'),
        ('hydroponic', 'Hydroponic'),
        ('mixed', 'Mixed')
    ], validators=[DataRequired()])
    years_experience = IntegerField('Years of Farming Experience', validators=[DataRequired(), NumberRange(min=0, max=100)])
    
    # Contact and profile
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    bio = TextAreaField('Personal Bio', validators=[Optional(), Length(max=500)])
    farm_description = TextAreaField('Farm Description', validators=[DataRequired(), Length(min=20, max=1000)])
    certifications = TextAreaField('Certifications (Optional)', validators=[Optional(), Length(max=500)])
    
    # Profile image
    profile_image = FileField('Profile Photo/Farm Logo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    
    submit = SubmitField('Update Profile')

class ProductSearchForm(FlaskForm):
    search = StringField('Search Products')
    category_id = SelectField('Category', coerce=int, choices=[])
    min_price = FloatField('Min Price', validators=[Optional(), NumberRange(min=0)])
    max_price = FloatField('Max Price', validators=[Optional(), NumberRange(min=0)])
    organic_only = BooleanField('Organic Only')
    in_stock_only = BooleanField('In Stock Only', default=True)
    sort_by = SelectField('Sort By', choices=[
        ('name', 'Name A-Z'),
        ('name_desc', 'Name Z-A'),
        ('price', 'Price Low to High'),
        ('price_desc', 'Price High to Low'),
        ('newest', 'Newest First'),
        ('rating', 'Highest Rated')
    ], default='newest')
    submit = SubmitField('Search')

class ProductReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars')
    ], coerce=int, validators=[DataRequired()])
    comment = TextAreaField('Review Comment', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Review')
