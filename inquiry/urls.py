from django.urls import path
from .views import index, download_pdf, health_check

urlpatterns = [
    path('', index, name='index'),
    path('submit', index, name='submit'),
    path('download-pdf/<int:inquiry_id>/', download_pdf, name='download_pdf'),
    path('health/', health_check, name='health_check'),
]
