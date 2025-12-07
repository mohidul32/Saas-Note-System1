# SaaS Notes System - Complete Implementation Guide

## 🎯 Project Overview

A full-stack multi-tenant SaaS Notes system with Django/DRF backend, React frontend, and MySQL database.

### Features
- ✅ Multi-tenant architecture (Companies → Workspaces → Notes)
- ✅ Public/Private notes with draft mode
- ✅ Voting system (upvotes/downvotes)
- ✅ 7-day auto-cleanup history system
- ✅ Tag management
- ✅ Role-based access control (Owner/Member)
- ✅ JWT authentication
- ✅ Search and sorting
- ✅ History tracking and restore

---

## 📋 Prerequisites

- Python 3.9+
- Node.js 16+
- MySQL 8.0+
- Redis (for Celery)

---

## 🚀 BACKEND SETUP (Step-by-Step)

### Step 1: Database Setup

```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE saas_notes_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user (optional)
CREATE USER 'saas_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON saas_notes_db.* TO 'saas_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 2: Clone/Create Project Structure

```bash
# Create project directory
mkdir saas-notes-system
cd saas-notes-system

# Create backend directory
mkdir backend
cd backend
```

### Step 3: Setup Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
# Save requirements.txt (from artifact above)
# Then install
pip install -r requirements.txt
```

### Step 5: Create Django Project

```bash
# Create Django project
django-admin startproject config .

# Create apps
python manage.py startapp users
python manage.py startapp companies
python manage.py startapp workspaces
python manage.py startapp notes
python manage.py startapp common

# Organize into apps directory
mkdir apps
mv users companies workspaces notes common apps/
```

### Step 6: Configure Settings

Create `.env` file in backend root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=saas_notes_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

Copy all the files from artifacts:
- `config/settings.py`
- `config/urls.py`
- `config/celery.py`
- All model files to respective apps
- All serializer, view, and permission files

### Step 7: Update `__init__.py` Files

In each app directory (`apps/users/`, `apps/companies/`, etc.), create or update `__init__.py`:

```python
default_app_config = 'apps.appname.apps.AppnameConfig'
```

Update `config/__init__.py`:

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### Step 8: Run Migrations

```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Step 9: Seed Database

```bash
# Create scripts directory
mkdir scripts

# Save seed_data.py to scripts/
# Run seeder
python scripts/seed_data.py
```

This will create:
- 50 companies
- 250 users (5 per company)
- 1,000 workspaces (20 per company)
- 500,000 notes (500 per workspace)
- 100 tags
- Thousands of votes

**Login credentials for testing:**
- Email: `owner.company-slug@example.com`
- Password: `password123`

### Step 10: Start Celery (for history cleanup)

In a separate terminal:

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start Celery worker
celery -A config worker -l info

# Start Celery beat (scheduler) - in another terminal
celery -A config beat -l info
```

### Step 11: Start Django Server

```bash
python manage.py runserver
```

Backend will be available at: `http://localhost:8000`

---

## 🎨 FRONTEND SETUP

### Step 1: Create React App

```bash
# From project root
cd ..  # Go back to project root
npx create-react-app frontend
cd frontend
```

### Step 2: Install Dependencies

```bash
npm install axios react-router-dom @tanstack/react-query
```

### Step 3: Copy Frontend Files

Copy all files from the artifacts:
- `src/App.js`
- `src/App.css`
- `src/services/api.js`
- `src/pages/*.js`
- `src/components/*.js`

Create directories:
```bash
mkdir src/pages
mkdir src/components
mkdir src/services
```

### Step 4: Create .env File

Create `.env` in frontend root:

```env
REACT_APP_API_URL=http://localhost:8000/api
```

### Step 5: Update package.json

Add proxy to package.json:

```json
{
  "proxy": "http://localhost:8000"
}
```

### Step 6: Start React App

```bash
npm start
```

Frontend will be available at: `http://localhost:3000`

---

## 📊 Database Schema

### ER Diagram

```
┌─────────────┐
│   Company   │
└──────┬──────┘
       │
       │ 1:N
       │
┌──────▼──────┐       ┌─────────────┐
│  Workspace  │       │     User    │
└──────┬──────┘       └──────┬──────┘
       │                     │
       │ 1:N            1:N  │
       │                     │
┌──────▼──────────────────────▼────┐
│             Note                 │
└──────┬────────┬─────────┬────────┘
       │        │         │
   1:N │    N:M │     1:N │
       │        │         │
 ┌─────▼──┐ ┌──▼───┐ ┌───▼────────┐
 │NoteHist│ │ Tag  │ │   Vote     │
 └────────┘ └──────┘ └────────────┘
```

### Key Tables

**companies**
- id, name, slug, description, created_at, updated_at, is_active

**users**
- id, email, username, first_name, last_name, role, company_id, is_active, date_joined

**workspaces**
- id, name, slug, description, company_id, created_by_id, created_at, updated_at

**notes**
- id, title, content, note_type, is_draft, workspace_id, created_by_id, updated_by_id, created_at, updated_at

**tags**
- id, name, created_at

**notes_tags** (many-to-many)
- note_id, tag_id

**votes**
- id, note_id, user_id, company_id, vote_type, created_at

**note_history**
- id, note_id, title, content, changed_by_id, changed_at

---

## 🔐 Security Features

1. **JWT Authentication**: Access and refresh tokens
2. **Role-Based Access Control**: Owner vs Member permissions
3. **CSRF Protection**: Django CSRF middleware
4. **SQL Injection Prevention**: Django ORM parameterized queries
5. **XSS Protection**: React auto-escaping
6. **HTTPS Ready**: SSL redirect settings for production
7. **Input Validation**: DRF serializers
8. **Rate Limiting**: Can be added with django-ratelimit

---

## ⚡ Performance Optimizations

### Database
- **Indexes** on frequently queried fields (company_id, note_type, created_at, etc.)
- **select_related()** for foreign keys
- **prefetch_related()** for many-to-many
- **Bulk operations** for seeding

### API
- **Pagination**: 50 items per page
- **Query optimization**: Annotated vote counts
- **Caching**: Can add Redis for public notes

### Frontend
- **React Query**: Automatic caching and refetching
- **Lazy Loading**: Code splitting with React.lazy() (can be added)

---

## 🔄 History Cleanup System

### How It Works

1. **Automatic Tracking**: Every note update creates a history entry
2. **Celery Beat Scheduler**: Runs cleanup task daily at 2 AM
3. **7-Day Retention**: Deletes history older than 7 days
4. **Restore Feature**: Users can restore from any available history

### Manual Cleanup

```python
# In Django shell
python manage.py shell

>>> from apps.notes.models import NoteHistory
>>> deleted_count = NoteHistory.cleanup_old_history()
>>> print(f"Deleted {deleted_count} old entries")
```

---

## 🧪 Testing

### Test Seeded Data

```bash
# Get all companies
curl http://localhost:8000/api/companies/

# Login
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"owner.acme-corp@example.com","password":"password123"}'

# Get public notes
curl http://localhost:8000/api/notes/public_notes/

# Get my notes (with token)
curl http://localhost:8000/api/notes/my_notes/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📁 Complete File Structure

```
saas-notes-system/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── celery.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── users/
│   │   │   ├── models.py
│   │   │   ├── admin.py
│   │   │   └── apps.py
│   │   ├── companies/
│   │   │   ├── models.py
│   │   │   └── ...
│   │   ├── workspaces/
│   │   │   ├── models.py
│   │   │   └── ...
│   │   ├── notes/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── permissions.py
│   │   │   ├── tasks.py
│   │   │   └── admin.py
│   │   └── common/
│   └── scripts/
│       └── seed_data.py
├── frontend/
│   ├── package.json
│   ├── .env
│   ├── public/
│   └── src/
│       ├── App.js
│       ├── App.css
│       ├── index.js
│       ├── services/
│       │   └── api.js
│       ├── components/
│       │   ├── Navigation.js
│       │   ├── NoteCard.js
│       │   └── SearchBar.js
│       └── pages/
│           ├── PublicNotesPage.js
│           ├── MyNotesPage.js
│           ├── NoteEditorPage.js
│           ├── NoteDetailPage.js
│           └── LoginPage.js
└── README.md
```

---

## 🐛 Common Issues & Solutions

### Issue: MySQL Connection Error
**Solution**: Check MySQL is running and credentials in .env are correct

### Issue: Celery not starting
**Solution**: Ensure Redis is installed and running: `redis-server`

### Issue: CORS errors
**Solution**: Check CORS_ALLOWED_ORIGINS in settings.py and frontend proxy

### Issue: Migration errors
**Solution**: Delete migrations and db, recreate:
```bash
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

---

## 🚀 Production Deployment Checklist

1. ✅ Set DEBUG=False
2. ✅ Use strong SECRET_KEY
3. ✅ Configure ALLOWED_HOSTS
4. ✅ Setup PostgreSQL (replace MySQL)
5. ✅ Configure static files (collectstatic)
6. ✅ Setup Gunicorn/uWSGI
7. ✅ Configure Nginx reverse proxy
8. ✅ Enable HTTPS
9. ✅ Setup environment variables
10. ✅ Configure Redis for caching
11. ✅ Setup monitoring (Sentry)
12. ✅ Database backups
13. ✅ Setup CI/CD pipeline

---

## 📞 Support

For issues or questions:
- Review error logs
- Check Django debug toolbar
- Use browser DevTools for frontend issues
- Review Celery logs for background tasks

---

## ✅ Completion Checklist

- [ ] MySQL database created
- [ ] Backend virtual environment setup
- [ ] All dependencies installed
- [ ] Django migrations applied
- [ ] Superuser created
- [ ] Database seeded with test data
- [ ] Celery worker running
- [ ] Celery beat running
- [ ] Django server running (port 8000)
- [ ] React frontend created
- [ ] Frontend dependencies installed
- [ ] React server running (port 3000)
- [ ] Can login with seeded credentials
- [ ] Can view public notes
- [ ] Can create/edit notes
- [ ] Can vote on notes
- [ ] Can view and restore history

---

**Your SaaS Notes System is now complete and ready to use!** 🎉