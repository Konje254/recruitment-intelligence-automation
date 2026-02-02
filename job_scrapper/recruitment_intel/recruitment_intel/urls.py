from django.contrib import admin
from django.urls import path
from scraper import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.dashboard, name="dashboard"),
    path("companies/<int:company_id>/", views.company_detail, name="company_detail"),
]
