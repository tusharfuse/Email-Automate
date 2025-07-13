web: python manage.py install_playwright && python manage.py collectstatic --noinput && gunicorn missingclaims.wsgi --bind 0.0.0.0:${PORT:-10000} --timeout 120 --workers 1
