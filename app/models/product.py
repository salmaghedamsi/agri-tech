from datetime import datetime
from app import db

class ProductCategory(db.Model):
    __tablename__ = 'product_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<ProductCategory {self.name}>'

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(20), default='kg')  # kg, piece, liter, etc.
    image = db.Column(db.String(255))  # Main product image filename
    image_url = db.Column(db.String(255))  # Primary image
    images = db.Column(db.Text)  # JSON array of additional images
    is_organic = db.Column(db.Boolean, default=False)
    is_available = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    harvest_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    min_order_quantity = db.Column(db.Integer, default=1)
    delivery_available = db.Column(db.Boolean, default=False)
    delivery_radius = db.Column(db.Integer)  # in km
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'), nullable=False)
    
    # Relationships
    reviews = db.relationship('ProductReview', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)
    
    def get_total_reviews(self):
        """Get total number of reviews"""
        return self.reviews.count()
    
    def get_all_images(self):
        """Get all product images including primary and additional images"""
        images_list = []
        if self.image:
            images_list.append(self.image)
        if self.image_url:
            images_list.append(self.image_url)
        if self.images:
            import json
            try:
                additional_images = json.loads(self.images)
                images_list.extend(additional_images)
            except:
                pass
        return images_list
    
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.is_available and self.quantity > 0
    
    def get_stock_status(self):
        """Get stock status as string"""
        if not self.is_available:
            return "Unavailable"
        elif self.quantity <= 0:
            return "Out of Stock"
        elif self.quantity <= 5:
            return "Low Stock"
        else:
            return "In Stock"
    
    def formatted_price(self):
        """Get formatted price string"""
        return f"${self.price:.2f}/{self.unit}"
    
    def __repr__(self):
        return f'<Product {self.name}>'

class ProductReview(db.Model):
    __tablename__ = 'product_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<ProductReview {self.rating} stars>'
