from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from . import views

urlpatterns = [
    path('api/schedule_emails/', views.schedule_emails, name='schedule_emails'),
    path('api/email-status/', views.get_email_status, name='get_email_status'),
]