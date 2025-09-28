#!/usr/bin/env python3
"""
Test script to check if enrollment functionality works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.course import Course, CourseEnrollment
from app.models.user import User

def test_enrollment():
    app = create_app()
    
    with app.app_context():
        try:
            # Check if we have courses
            courses = Course.query.filter_by(is_published=True).all()
            print(f"Found {len(courses)} published courses")
            
            if courses:
                course = courses[0]
                print(f"Testing with course: {course.title}")
                
                # Check if we have users
                users = User.query.filter_by(user_type='farmer').all()
                print(f"Found {len(users)} farmers")
                
                if users:
                    user = users[0]
                    print(f"Testing with user: {user.username}")
                    
                    # Check existing enrollment
                    existing = CourseEnrollment.query.filter_by(
                        course_id=course.id,
                        user_id=user.id
                    ).first()
                    
                    if existing:
                        print("User is already enrolled")
                    else:
                        print("User is not enrolled - enrollment should work")
                        
                        # Test enrollment
                        enrollment = CourseEnrollment(
                            user_id=user.id,
                            course_id=course.id
                        )
                        db.session.add(enrollment)
                        db.session.commit()
                        print("Enrollment successful!")
                else:
                    print("No farmers found in database")
            else:
                print("No published courses found")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_enrollment()


