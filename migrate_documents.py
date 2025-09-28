#!/usr/bin/env python3
"""
Migration script to add document management fields to the courses table.
Run this script to update your existing database with the new fields.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.course import Course

def migrate_documents():
    """Add document management fields to courses table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if the columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('courses')]
            
            if 'document_path' not in columns:
                print("Adding document_path column...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE courses ADD COLUMN document_path VARCHAR(500)"))
                    conn.commit()
                print("✓ document_path column added")
            else:
                print("✓ document_path column already exists")
            
            if 'tutorial_video_url' not in columns:
                print("Adding tutorial_video_url column...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE courses ADD COLUMN tutorial_video_url VARCHAR(500)"))
                    conn.commit()
                print("✓ tutorial_video_url column added")
            else:
                print("✓ tutorial_video_url column already exists")
            
            print("\n🎉 Migration completed successfully!")
            print("You can now use the course management system with document uploads.")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting course document migration...")
    success = migrate_documents()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("You can now:")
        print("1. Create courses with document uploads")
        print("2. Manage your courses at /learning/manage-courses")
        print("3. Upload PDFs, Word docs, and other materials")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)
