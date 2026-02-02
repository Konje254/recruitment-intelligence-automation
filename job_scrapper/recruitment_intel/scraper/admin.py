from django.contrib import admin
from .models import Platform, ScrapeRun, Company, JobPosting, JobSource

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

@admin.register(ScrapeRun)
class ScrapeRunAdmin(admin.ModelAdmin):
    list_display = ("id", "platform", "status", "started_at", "finished_at", "requested_limit")

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "website_url", "email")
    search_fields = ("name", "email")

class JobSourceInline(admin.TabularInline):
    model = JobSource
    extra = 0

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "company", "location", "created_at")
    search_fields = ("title", "company__name", "location")
    inlines = [JobSourceInline]
