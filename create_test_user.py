#!/usr/bin/env python3
"""
Create test user for AgriConnect
"""

from app import create_app, db
from app.models.user import User

def create_test_user():
    """Create test user with email rima@gmail.com and password rima00"""
    app = create_app()
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Check if user already exists
        existing_user = User.query.filter_by(email='rima@gmail.com').first()
        if existing_user:
            print("Test user already exists!")
            return
        
        # Create test user
        user = User(
            username='rima',
            email='rima@gmail.com',
            first_name='Rima',
            last_name='Test',
            phone='+21612345678',
            location='Tunisia',
            user_type='farmer'
        )
        user.set_password('rima00')
        
        db.session.add(user)
        db.session.commit()
        
        print("✅ Test user created successfully!")
        print("Email: rima@gmail.com")
        print("Password: L is missing ")
        print("User Type: Farmer")

if __name__ == '__main__':
    create_test_user()
