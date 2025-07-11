# Running the Django Project on Windows

Gunicorn is not supported natively on Windows, which causes the error:
```
bash: line 1: gunicorn: command not found
```

To run the Django project locally on Windows, use the built-in Django development server:

```bash
python manage.py runserver
```

This will start the development server at http://127.0.0.1:8000/

If you want to use Gunicorn, consider running your project inside WSL (Windows Subsystem for Linux) or a Linux-based Docker container.

For production deployment, Gunicorn should be run on a Linux server or compatible environment.
