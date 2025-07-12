from django.contrib import admin
from .models import Inquiry

class InquiryAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'claims_type', 'provider_name', 'created_at')
    list_filter = ('created_at',)

admin.site.register(Inquiry, InquiryAdmin)
