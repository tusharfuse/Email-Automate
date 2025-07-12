# Deployment Instructions for Render

This document provides the steps to install dependencies and deploy the Django project on Render.

## Prerequisites

- Python 3.8 or higher installed locally
- Git installed
- Render account and a new Web Service created

## Local Setup

1. Create and activate a Python virtual environment:

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run database migrations:

```bash
python manage.py migrate
```

4. Collect static files:

```bash
python manage.py collectstatic --noinput
```

5. Run the development server locally:

```bash
python manage.py runserver
```

## Render Deployment Setup

1. Push your code to a Git repository connected to Render.

2. In Render dashboard, create a new Web Service with the following settings:

- Environment: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `python manage.py collectstatic --noinput && gunicorn missingclaims.wsgi`

3. Set environment variables in Render:

- `DJANGO_SECRET_KEY`: Your Django secret key (use a secure random string)
- `DJANGO_DEBUG`: `False`
- `DATABASE_URL`: (optional) If using a production database like Postgres, set the connection URL here.

4. Ensure your `ALLOWED_HOSTS` in `settings.py` includes your Render service URL.

5. Deploy the service. Render will install dependencies, collect static files, and start Gunicorn.

## Notes

- The project uses Whitenoise for static file serving.
- For production, ensure DEBUG is set to False and SECRET_KEY is kept secret.
- SQLite is used by default; consider using a production database for scalability.

## Troubleshooting

- Check Render logs for errors.
- Verify environment variables are correctly set.
- Ensure static files are collected and served properly.

---

These instructions should help you install everything and deploy the Django project on Render.
