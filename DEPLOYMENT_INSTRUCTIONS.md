# Deployment Instructions

## Running Playwright Install Command

After deploying the application, you need to run the following Django management command to install Playwright browser binaries:

```bash
python manage.py install_playwright
```

### Automating in Render Deployment

To automate this step in Render deployment, add the following command to your Render build or start script:

```bash
python manage.py install_playwright
```

For example, if you have a `start` script in your `Procfile` or Render settings, you can prepend this command:

```
python manage.py install_playwright && gunicorn missingclaims.wsgi
```

This ensures that Playwright browsers are installed automatically on each deployment, preventing PDF generation errors related to missing browser executables.

---

Please make sure to commit and push these changes before deploying.
