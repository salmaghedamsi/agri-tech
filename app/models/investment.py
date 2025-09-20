from datetime import datetime
from app import db

class Investment(db.Model):
    __tablename__ = 'investments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    investment_type = db.Column(db.Enum('equity', 'debt', 'revenue_share', 'land_lease'), nullable=False)
    amount_requested = db.Column(db.Float, nullable=False)
    amount_raised = db.Column(db.Float, default=0.0)
    minimum_investment = db.Column(db.Float, nullable=False)
    maximum_investment = db.Column(db.Float)
    interest_rate = db.Column(db.Float)  # For debt investments
    expected_return = db.Column(db.Float)  # Expected annual return percentage
    duration_months = db.Column(db.Integer)  # Investment duration
    risk_level = db.Column(db.Enum('low', 'medium', 'high'), default='medium')
    status = db.Column(db.Enum('draft', 'active', 'funded', 'completed', 'cancelled'), default='draft')
    target_date = db.Column(db.Date)  # Fundraising target date
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    proposals = db.relationship('InvestmentProposal', backref='investment', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_funding_percentage(self):
        """Calculate funding percentage"""
        if self.amount_requested == 0:
            return 0
        return (self.amount_raised / self.amount_requested) * 100
    
    def get_remaining_amount(self):
        """Get remaining amount to be raised"""
        return self.amount_requested - self.amount_raised
    
    def is_fully_funded(self):
        """Check if investment is fully funded"""
        return self.amount_raised >= self.amount_requested
    
    def get_risk_color(self):
        """Get color based on risk level"""
        color_map = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger'
        }
        return color_map.get(self.risk_level, 'info')
    
    def __repr__(self):
        return f'<Investment {self.title}>'

class InvestmentProposal(db.Model):
    __tablename__ = 'investment_proposals'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.Enum('pending', 'accepted', 'rejected', 'withdrawn'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    investment_id = db.Column(db.Integer, db.ForeignKey('investments.id'), nullable=False)
    investor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def get_status_color(self):
        """Get color based on proposal status"""
        color_map = {
            'pending': 'warning',
            'accepted': 'success',
            'rejected': 'danger',
            'withdrawn': 'secondary'
        }
        return color_map.get(self.status, 'info')
    
    def __repr__(self):
        return f'<InvestmentProposal {self.investor.username} - {self.amount}>'
