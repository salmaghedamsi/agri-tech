#!/usr/bin/env python3
"""
AgriConnect Startup Script
Simple script to initialize and run the AgriConnect application
"""

import os
import sys
from app import create_app, db
from app.models import *

def create_sample_data():
    """Create sample data for demonstration"""
    print("Creating sample data...")
    
    # Create product categories
    categories = [
        {'name': 'Vegetables', 'description': 'Fresh vegetables and greens'},
        {'name': 'Fruits', 'description': 'Fresh fruits and berries'},
        {'name': 'Grains', 'description': 'Cereals and grain products'},
        {'name': 'Herbs & Spices', 'description': 'Culinary herbs and spices'},
        {'name': 'Organic Products', 'description': 'Certified organic products'},
        {'name': 'Seeds & Plants', 'description': 'Seeds, seedlings, and plants'}
    ]
    
    for cat_data in categories:
        category = ProductCategory.query.filter_by(name=cat_data['name']).first()
        if not category:
            category = ProductCategory(
                name=cat_data['name'],
                description=cat_data['description']
            )
            db.session.add(category)
    
    # Create forum categories
    forum_categories = [
        {'name': 'General Discussion', 'description': 'General farming discussions', 'icon': 'fas fa-comments', 'color': '#007bff'},
        {'name': 'Crop Management', 'description': 'Crop growing and management tips', 'icon': 'fas fa-seedling', 'color': '#28a745'},
        {'name': 'Weather & Climate', 'description': 'Weather discussions and climate adaptation', 'icon': 'fas fa-cloud-sun', 'color': '#17a2b8'},
        {'name': 'Technology & IoT', 'description': 'Smart farming and IoT discussions', 'icon': 'fas fa-microchip', 'color': '#6f42c1'},
        {'name': 'Market & Pricing', 'description': 'Market trends and pricing discussions', 'icon': 'fas fa-chart-line', 'color': '#fd7e14'},
        {'name': 'Investment & Finance', 'description': 'Agricultural investment discussions', 'icon': 'fas fa-dollar-sign', 'color': '#20c997'}
    ]
    
    for cat_data in forum_categories:
        category = ForumCategory.query.filter_by(name=cat_data['name']).first()
        if not category:
            category = ForumCategory(
                name=cat_data['name'],
                description=cat_data['description'],
                icon=cat_data['icon'],
                color=cat_data['color']
            )
            db.session.add(category)
    
    db.session.commit()
    print("Sample data created successfully!")

def main():
    """Main startup function"""
    print("🌱 Starting AgriConnect - Smart Farming Platform")
    print("=" * 50)
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        # Create database tables
        print("Creating database tables...")
        db.create_all()
        
        # Create sample data
        create_sample_data()
        
        print("\n✅ Database initialized successfully!")
        print("\n🚀 Starting AgriConnect server...")
        print("📍 Application will be available at: http://localhost:5000")
        print("🔧 Admin panel: http://localhost:5000/admin")
        print("📚 API documentation: http://localhost:5000/api")
        print("\n" + "=" * 50)
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
