# Database Setup Guide

## For New Developers (First Time Setup)

When you clone this repository, follow these steps to set up your local database:

### 1. Clone and Setup Environment
```bash
git clone https://github.com/salmaghedamsi/agri-tech.git
cd agri-tech
python -m venv venv
venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```

### 2. Setup Database
```bash
python setup_database.py
```

This script will:
- Create the instance directory
- Run all database migrations
- Set up the proper schema
- Optionally create sample data

### 3. Start Application
```bash
python run.py
```

## For Developers Adding New Database Changes

When you add new models or modify existing ones:

### 1. Create Migration
```bash
flask db migrate -m "Description of your changes"
```

### 2. Review Migration File
Check the generated migration in `migrations/versions/` and verify it's correct.

### 3. Apply Migration
```bash
flask db upgrade
```

### 4. Commit Changes
```bash
git add migrations/
git commit -m "Add migration for [your changes]"
git push
```

## For Developers Pulling Database Changes

When someone else adds database changes:

### 1. Pull Latest Code
```bash
git pull origin main
```

### 2. Apply New Migrations
```bash
flask db upgrade
```

## Migration Commands Reference

- `flask db init` - Initialize migrations (done once)
- `flask db migrate -m "message"` - Create new migration
- `flask db upgrade` - Apply migrations
- `flask db downgrade` - Rollback migration
- `flask db history` - Show migration history
- `flask db current` - Show current migration

## Database Files to Ignore

These files should NEVER be committed:
- `instance/` - Contains local database files
- `*.db` - SQLite database files
- `*.sqlite` - SQLite database files

## Troubleshooting

### Column doesn't exist error
```bash
flask db upgrade
```

### Migration conflicts
```bash
flask db merge -m "Merge migrations"
```

### Reset database (DANGER - loses all data)
```bash
rm instance/agriconnect.db
flask db upgrade
python setup_database.py
```

## Production Deployment

For production, use proper database migrations:
```bash
flask db upgrade
```

Never delete the migrations folder or database files in production!