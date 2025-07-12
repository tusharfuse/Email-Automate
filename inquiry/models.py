from django.db import models

class Inquiry(models.Model):
    client_name = models.CharField(max_length=255)
    claims_type = models.CharField(max_length=255)
    provider_name = models.CharField(max_length=255)
    tax_id = models.CharField(max_length=50)
    npi = models.CharField(max_length=50)
    administrator = models.CharField(max_length=255, default='Patrick McCullough')
    telephone = models.CharField(max_length=50, default='(410) 850-8500')
    telefax = models.CharField(max_length=50, default='(410) 850-8655')
    email = models.EmailField(default='planoffice@mmpplans.com')
    created_at = models.DateTimeField(auto_now_add=True)
    patients = models.JSONField(blank=True, null=True)  # Store patients and claims as JSON
