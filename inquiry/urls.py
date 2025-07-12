from django.urls import path
from .views import index, download_pdf

urlpatterns = [
    path('', index, name='index'),
    path('submit', index, name='submit'),
    path('download-pdf/<int:inquiry_id>/', download_pdf, name='download_pdf'),
]
