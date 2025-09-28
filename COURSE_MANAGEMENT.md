# Course Management System

## Overview

The course management system allows agricultural experts to create, manage, and publish courses with document uploads and tutorial videos.

## Features

### For Agricultural Experts:

- **Create Courses**: Upload documents (PDF, DOC, DOCX, TXT) and tutorial videos
- **Manage Courses**: Edit, publish/unpublish, and delete courses
- **File Management**: Secure file uploads with organized storage
- **Course Dashboard**: View statistics and manage all courses in one place

### For Students:

- **Browse Courses**: Search and filter published courses
- **Enroll in Courses**: Access course materials and videos
- **Track Progress**: Monitor learning progress through modules

## Database Schema

### Courses Table

- `id`: Primary key
- `title`: Course title
- `description`: Course description
- `price`: Course price (0 for free)
- `duration_hours`: Course duration
- `difficulty_level`: beginner, intermediate, advanced
- `language`: en, ar, fr
- `is_published`: Publication status
- `document_path`: Path to uploaded documents
- `tutorial_video_url`: URL to tutorial videos
- `instructor_id`: Foreign key to users table
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## File Structure

```
agriconnect/
├── app/
│   ├── models/
│   │   └── course.py          # Course models
│   ├── routes/
│   │   └── learning.py        # Course management routes
│   ├── forms/
│   │   └── course.py          # Course forms
│   └── templates/
│       └── learning/
│           ├── course_management.html
│           ├── create_course.html
│           └── edit_course.html
├── static/
│   └── uploads/
│       └── courses/
│           └── documents/      # Uploaded course documents
└── migrate_documents.py       # Database migration script
```

## Usage

### 1. Access Course Management

- Navigate to `/learning/manage-courses`
- Only experts can access this page

### 2. Create a New Course

- Click "Create New Course"
- Fill in course details
- Upload documents and add tutorial video URLs
- Choose to publish immediately or save as draft

### 3. Manage Existing Courses

- View all your courses in the dashboard
- Edit course details and uploads
- Publish/unpublish courses
- Delete courses (with confirmation)

### 4. File Uploads

- Documents are stored in `static/uploads/courses/documents/`
- Supported formats: PDF, DOC, DOCX, TXT
- Files are organized by course ID
- Secure filename handling

## API Endpoints

### Course Management

- `GET /learning/manage-courses` - Course management dashboard
- `GET /learning/courses/create` - Create course form
- `POST /learning/courses/create` - Create course
- `GET /learning/courses/<id>/edit` - Edit course form
- `POST /learning/courses/<id>/edit` - Update course
- `POST /learning/courses/<id>/delete` - Delete course
- `POST /learning/courses/<id>/publish` - Toggle publication

### Student Access

- `GET /learning/` - Browse published courses
- `GET /learning/course/<id>` - Course detail page
- `POST /learning/course/<id>/enroll` - Enroll in course
- `GET /learning/my-courses` - User's enrolled courses

## Security Features

- **File Validation**: Only allowed file types can be uploaded
- **Secure Filenames**: Uploaded files are sanitized
- **Access Control**: Only experts can manage courses
- **Ownership Verification**: Users can only edit their own courses

## Installation

1. Run the migration script:

   ```bash
   python migrate_documents.py
   ```

2. Create upload directories:

   ```bash
   mkdir -p static/uploads/courses/documents
   ```

3. Start the application:
   ```bash
   python run.py
   ```

## Future Enhancements

- [ ] Cloud storage integration (AWS S3, Google Drive)
- [ ] Video upload support (not just URLs)
- [ ] Course categories and tags
- [ ] Advanced analytics and reporting
- [ ] Course templates
- [ ] Bulk course operations
- [ ] Course versioning
- [ ] Student progress tracking
- [ ] Course completion certificates

