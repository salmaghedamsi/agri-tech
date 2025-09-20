from datetime import datetime
from app import db

class Land(db.Model):
    __tablename__ = 'lands'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    area_acres = db.Column(db.Float, nullable=False)
    price_per_acre = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    land_type = db.Column(db.Enum('agricultural', 'residential', 'commercial', 'mixed'), default='agricultural')
    soil_type = db.Column(db.String(100))
    water_source = db.Column(db.String(100))
    infrastructure = db.Column(db.Text)  # Roads, electricity, water, etc.
    images = db.Column(db.Text)  # JSON array of image URLs
    is_available = db.Column(db.Boolean, default=True)
    listing_type = db.Column(db.Enum('sale', 'lease', 'both'), default='sale')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    investments = db.relationship('LandInvestment', backref='land', lazy='dynamic', cascade='all, delete-orphan')
    leases = db.relationship('LandLease', backref='land', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_available_for_sale(self):
        """Check if land is available for sale"""
        return self.is_available and self.listing_type in ['sale', 'both']
    
    def get_available_for_lease(self):
        """Check if land is available for lease"""
        return self.is_available and self.listing_type in ['lease', 'both']
    
    def __repr__(self):
        return f'<Land {self.title}>'

class LandInvestment(db.Model):
    __tablename__ = 'land_investments'
    
    id = db.Column(db.Integer, primary_key=True)
    investment_amount = db.Column(db.Float, nullable=False)
    ownership_percentage = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum('pending', 'approved', 'rejected', 'completed'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    land_id = db.Column(db.Integer, db.ForeignKey('lands.id'), nullable=False)
    investor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<LandInvestment {self.investor.username} - {self.land.title}>'

class LandLease(db.Model):
    __tablename__ = 'land_leases'
    
    id = db.Column(db.Integer, primary_key=True)
    monthly_rent = db.Column(db.Float, nullable=False)
    lease_duration_months = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('pending', 'active', 'expired', 'terminated'), default='pending')
    terms_conditions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    land_id = db.Column(db.Integer, db.ForeignKey('lands.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<LandLease {self.tenant.username} - {self.land.title}>'
