# Django Quick Start Guide

Welcome to the AutoPhone Django project! This guide will help you get the Django application up and running quickly.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Git (for cloning the repository)
- A terminal or command prompt

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/calebmills99/AutoPhone.git
cd AutoPhone
```

### 2. Create a Virtual Environment (Recommended)

Creating a virtual environment helps isolate project dependencies:

**On Windows:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Install all required Python packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install Django along with other project dependencies.

## Django Project Setup

### 4. Verify Installation

Check that Django is installed correctly:

```bash
python manage.py --version
```

This should display the Django version (4.2.x).

### 5. Run Database Migrations

Django uses a database to store application data. Run the initial migrations:

```bash
python manage.py migrate
```

This creates the necessary database tables for Django's built-in features.

### 6. Create a Superuser (Optional but Recommended)

Create an admin account to access the Django admin interface:

```bash
python manage.py createsuperuser
```

Follow the prompts to set:
- Username
- Email address (optional)
- Password

### 7. Start the Development Server

Run the Django development server:

```bash
python manage.py runserver
```

The server will start on `http://127.0.0.1:8000/` by default.

You should see output like:
```
Django version 4.2.x, using settings 'autophone_project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK (Windows) or CONTROL-C (macOS/Linux).
```

### 8. Access Your Application

Open your web browser and navigate to:

- **Main application:** http://127.0.0.1:8000/
- **Admin interface:** http://127.0.0.1:8000/admin/

You should see a welcome message on the main page. Log in to the admin interface using the superuser credentials you created in step 6.

**Note:** The project includes a sample `core` app with a basic view and test to demonstrate the Django setup is working correctly.

## Common Django Commands

Here are some essential Django management commands:

### Check for Issues
```bash
python manage.py check
```

### Run Tests
```bash
python manage.py test
```

### Create a New Django App
```bash
python manage.py startapp app_name
```

### Make Database Migrations
After changing models:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collect Static Files (for production)
```bash
python manage.py collectstatic
```

## Project Structure

```
AutoPhone/
├── autophone_project/      # Django project configuration
│   ├── __init__.py
│   ├── settings.py         # Project settings
│   ├── urls.py             # URL routing
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration
├── core/                   # Sample Django app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py            # Sample tests
│   ├── views.py            # Sample views
│   └── migrations/
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── QUICKSTART.md           # This guide
└── db.sqlite3             # SQLite database (created after migrations)
```

## Development Workflow

1. **Start your virtual environment** (if not already active)
2. **Run the development server**: `python manage.py runserver`
3. **Make changes** to your code
4. **Test your changes**: The development server auto-reloads when you save files
5. **Run tests**: `python manage.py test`
6. **Commit your changes** to version control

## Troubleshooting

### ImportError: No module named django

- Make sure you've activated your virtual environment
- Run `pip install -r requirements.txt` again

### Port Already in Use

If port 8000 is already in use, specify a different port:

```bash
python manage.py runserver 8080
```

### Database Locked Error

If you get a database locked error:
- Make sure only one Django process is running
- On Windows, check if your antivirus is locking the database file

### Permission Denied on manage.py (macOS/Linux)

Make the file executable:

```bash
chmod +x manage.py
```

## Next Steps

- **Read the Django documentation**: https://docs.djangoproject.com/
- **Create your first app**: `python manage.py startapp myapp`
- **Define models** in your app's `models.py`
- **Create views** in your app's `views.py`
- **Add URL patterns** to route requests
- **Create templates** for your views

## Additional Resources

- [Django Official Documentation](https://docs.djangoproject.com/)
- [Django Tutorial](https://docs.djangoproject.com/en/stable/intro/tutorial01/)
- [Django REST Framework](https://www.django-rest-framework.org/) (for building APIs)
- [Django Best Practices](https://django-best-practices.readthedocs.io/)

## Getting Help

If you encounter issues:

1. Check the Django documentation
2. Search for error messages online
3. Ask questions on [Stack Overflow](https://stackoverflow.com/questions/tagged/django)
4. Visit the [Django Forum](https://forum.djangoproject.com/)
5. Check the project's GitHub issues

---

**Happy Coding!** 🚀
