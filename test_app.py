#!/usr/bin/env python3
"""
AgriConnect Test Script
Simple test to verify the application works correctly
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    
    try:
        from app import create_app, db
        print("✅ App imports successful")
        
        from app.models.user import User
        from app.models.product import Product, ProductCategory
        from app.models.course import Course
        from app.models.land import Land
        from app.models.forum import ForumPost, ForumCategory
        from app.models.weather import WeatherData, WeatherAlert
        from app.models.iot import IoTDevice, IoTData
        from app.models.investment import Investment
        from app.models.mentoring import Mentor
        from app.models.chatbot import ChatSession, ChatMessage
        print("✅ Model imports successful")
        
        from app.forms.auth import LoginForm, RegisterForm
        from app.forms.product import ProductForm
        from app.forms.course import CourseForm
        print("✅ Form imports successful")
        
        from app.routes.auth import auth_bp
        from app.routes.dashboard import dashboard_bp
        from app.routes.marketplace import marketplace_bp
        from app.routes.learning import learning_bp
        from app.routes.mentoring import mentoring_bp
        from app.routes.investment import investment_bp
        from app.routes.weather import weather_bp
        from app.routes.community import community_bp
        from app.routes.admin import admin_bp
        from app.routes.api import api_bp
        print("✅ Route imports successful")
        
        from app.utils.weather import get_weather_data, create_mock_weather_data
        from app.utils.chatbot import get_ai_response, get_mock_response
        print("✅ Utility imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_creation():
    """Test if the Flask app can be created"""
    print("\nTesting app creation...")
    
    try:
        from app import create_app
        app = create_app()
        print("✅ Flask app created successfully")
        
        # Test if all blueprints are registered
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        expected_blueprints = ['auth', 'dashboard', 'marketplace', 'learning', 'mentoring', 'investment', 'weather', 'community', 'admin', 'api']
        
        for expected in expected_blueprints:
            if expected in blueprint_names:
                print(f"✅ Blueprint '{expected}' registered")
            else:
                print(f"❌ Blueprint '{expected}' not found")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False

def test_database_models():
    """Test if database models can be created"""
    print("\nTesting database models...")
    
    try:
        from app import create_app, db
        from app.models.user import User
        from app.models.product import Product, ProductCategory
        
        app = create_app()
        with app.app_context():
            # Test User model
            user = User(
                username='testuser',
                email='test@example.com',
                first_name='Test',
                last_name='User',
                user_type='farmer'
            )
            user.set_password('testpassword')
            print("✅ User model created")
            
            # Test ProductCategory model
            category = ProductCategory(
                name='Test Category',
                description='Test description'
            )
            print("✅ ProductCategory model created")
            
            # Test Product model
            product = Product(
                name='Test Product',
                description='Test product description',
                price=10.50,
                quantity=100,
                unit='kg',
                seller_id=1,
                category_id=1
            )
            print("✅ Product model created")
            
        return True
        
    except Exception as e:
        print(f"❌ Database model error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 AgriConnect Application Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_app_creation,
        test_database_models
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("\nTo start the application, run:")
        print("  python start.py")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
