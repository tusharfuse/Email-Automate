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

class Patient(models.Model):
    inquiry = models.ForeignKey(Inquiry, related_name='patients', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    dob = models.DateField()

class Claim(models.Model):
    patient = models.ForeignKey(Patient, related_name='claims', on_delete=models.CASCADE)
    date_of_service = models.CharField(max_length=50, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
