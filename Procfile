web: python manage.py collectstatic --noinput && gunicorn missingclaims.wsgi --bind 0.0.0.0:${PORT:-10000} --timeout 120 --workers 3
