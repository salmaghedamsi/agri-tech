#!/usr/bin/env python3
"""
Migration script to add new module management fields to the course_modules table.
Run this script to update your existing database with the new fields.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.course import CourseModule

def migrate_modules():
    """Add new module management fields to course_modules table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if the columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('course_modules')]
            
            # Add video_url column
            if 'video_url' not in columns:
                print("Adding video_url column...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE course_modules ADD COLUMN video_url VARCHAR(500)"))
                    conn.commit()
                print("✓ video_url column added")
            else:
                print("✓ video_url column already exists")
            
            # Add document_path column
            if 'document_path' not in columns:
                print("Adding document_path column...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE course_modules ADD COLUMN document_path VARCHAR(500)"))
                    conn.commit()
                print("✓ document_path column added")
            else:
                print("✓ document_path column already exists")
            
            # Add is_required column
            if 'is_required' not in columns:
                print("Adding is_required column...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE course_modules ADD COLUMN is_required BOOLEAN DEFAULT TRUE"))
                    conn.commit()
                print("✓ is_required column added")
            else:
                print("✓ is_required column already exists")
            
            # Add updated_at column
            if 'updated_at' not in columns:
                print("Adding updated_at column...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE course_modules ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
                    conn.commit()
                print("✓ updated_at column added")
            else:
                print("✓ updated_at column already exists")
            
            # Update content_type enum
            print("Updating content_type column...")
            with db.engine.connect() as conn:
                # For SQLite, create a new table with the desired schema
                conn.execute(db.text("""
                    CREATE TABLE course_modules_new (
                        id INTEGER PRIMARY KEY,
                        title VARCHAR(200) NOT NULL,
                        description TEXT,
                        content TEXT,
                        content_type VARCHAR(20) CHECK (
                            content_type IN (
                                'video', 'text', 'quiz', 'assignment', 
                                'document', 'video_plus_doc'
                            )
                        ),
                        video_url VARCHAR(500),
                        document_path VARCHAR(500),
                        duration_minutes INTEGER DEFAULT 0,
                        order_index INTEGER DEFAULT 0,
                        is_required BOOLEAN DEFAULT 1,
                        is_published BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        course_id INTEGER NOT NULL,
                        FOREIGN KEY (course_id) REFERENCES courses(id)
                    )
                """))
                
                # Copy data from old table
                conn.execute(db.text("""
                    INSERT INTO course_modules_new (
                        id, title, description, content, content_type,
                        duration_minutes, order_index, is_published,
                        created_at, course_id
                    )
                    SELECT id, title, description, content, content_type,
                           duration_minutes, order_index, is_published,
                           created_at, course_id
                    FROM course_modules
                """))
                
                # Drop old table and rename new table
                conn.execute(db.text("DROP TABLE course_modules"))
                conn.execute(db.text("ALTER TABLE course_modules_new RENAME TO course_modules"))
                
                conn.commit()
            print("✓ content_type column updated")
            
            print("\n🎉 Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting course module enhancements migration...")
    success = migrate_modules()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("The course module system now supports:")
        print("1. Video content with URL tracking")
        print("2. Document attachments")
        print("3. Required/optional module settings")
        print("4. More content types (video, text, quiz, assignment, document, video+doc)")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)