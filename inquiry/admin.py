from django.contrib import admin
from .models import Inquiry, Patient, Claim

class ClaimInline(admin.TabularInline):
    model = Claim
    extra = 1

class PatientInline(admin.TabularInline):
    model = Patient
    extra = 1

class PatientAdmin(admin.ModelAdmin):
    inlines = [ClaimInline]

class InquiryAdmin(admin.ModelAdmin):
    inlines = [PatientInline]
    list_display = ('client_name', 'claims_type', 'provider_name', 'created_at')
    list_filter = ('created_at',)

admin.site.register(Inquiry, InquiryAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Claim)
