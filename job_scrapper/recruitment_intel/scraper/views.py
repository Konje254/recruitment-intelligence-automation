from django.shortcuts import render, get_object_or_404
from .models import Company, JobPosting, ScrapeRun

def dashboard(request):
    companies = Company.objects.order_by("name")[:200]
    jobs = JobPosting.objects.select_related("company").order_by("-created_at")[:200]
    runs = ScrapeRun.objects.select_related("platform").order_by("-started_at")[:20]
    return render(request, "scraper/dashboard.html", {"companies": companies, "jobs": jobs, "runs": runs})

def company_detail(request, company_id: int):
    company = get_object_or_404(Company, id=company_id)
    jobs = company.jobs.order_by("-created_at")[:200]
    return render(request, "scraper/company_detail.html", {"company": company, "jobs": jobs})
