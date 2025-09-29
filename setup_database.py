#!/usr/bin/env python3
"""
Database setup script for new developers
Run this script after cloning the repository to set up the database properly
"""
import os
import sys
from flask import Flask
from flask_migrate import upgrade
from app import create_app, db

def setup_database():
    """Set up the database for a new developer environment"""
    
    print("Setting up AgriConnect Database...")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        try:
            # Check if instance directory exists, create if not
            instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
            if not os.path.exists(instance_dir):
                os.makedirs(instance_dir)
                print(f"✓ Created instance directory: {instance_dir}")
            
            # Run database migrations
            print("✓ Running database migrations...")
            upgrade()
            
            # Create all tables (in case migrations don't cover everything)
            db.create_all()
            
            print("✓ Database setup completed successfully!")
            print("\nNext steps:")
            print("1. Activate virtual environment: venv\\Scripts\\Activate.ps1")
            print("2. Run the application: python run.py")
            print("3. Visit: http://localhost:5000")
            
            return True
            
        except Exception as e:
            print(f"✗ Error setting up database: {str(e)}")
            return False

def create_sample_data():
    """Create sample data for development (optional)"""
    from app.models.user import User
    from app.models.product import ProductCategory
    
    with create_app().app_context():
        try:
            # Check if admin user exists
            admin = User.query.filter_by(email='admin@agriconnect.com').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@agriconnect.com',
                    first_name='Admin',
                    last_name='User',
                    user_type='admin',
                    is_active=True,
                    is_verified=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
            
            # Create basic product categories
            categories = [
                'Vegetables', 'Fruits', 'Grains', 'Dairy', 'Meat', 
                'Organic Products', 'Seeds', 'Tools', 'Fertilizers'
            ]
            
            for cat_name in categories:
                if not ProductCategory.query.filter_by(name=cat_name).first():
                    category = ProductCategory(
                        name=cat_name,
                        description=f"{cat_name} and related products"
                    )
                    db.session.add(category)
            
            db.session.commit()
            print("✓ Sample data created successfully!")
            
        except Exception as e:
            print(f"✗ Error creating sample data: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    print("=" * 50)
    print("AgriConnect Database Setup")
    print("=" * 50)
    
    if setup_database():
        # Ask if user wants sample data
        response = input("\nWould you like to create sample data? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            create_sample_data()
    
    print("\nSetup complete!")