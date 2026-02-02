import logging
from datetime import datetime
from typing import List

from django.db import transaction
from django.utils import timezone

from .models import Company, JobPosting, JobSource, Platform, ScrapeRun
from .utils import make_job_key
from .enrich import extract_email_from_company_page

log = logging.getLogger("scraper")

@transaction.atomic
def upsert_company(name: str, website_url: str = "", email: str = "") -> Company:
    obj, _ = Company.objects.get_or_create(name=name)
    changed = False
    if website_url and obj.website_url != website_url:
        obj.website_url = website_url
        changed = True
    if email and obj.email != email:
        obj.email = email
        changed = True
    if changed:
        obj.save()
    return obj

@transaction.atomic
def upsert_job(*, platform: Platform, title: str, company: Company, location: str, description: str, source_url: str) -> JobPosting:
    key = make_job_key(title, company.name, location)
    job = JobPosting.objects.filter(normalized_key=key).select_related("company").first()
    if not job:
        job = JobPosting.objects.create(
            title=title,
            company=company,
            location=location,
            description=description,
            normalized_key=key,
        )
    else:
        # Merge strategy: keep the "best" description (longest)
        if description and len(description) > len(job.description or ""):
            job.description = description
            job.save()

    JobSource.objects.get_or_create(job=job, platform=platform, source_url=source_url)
    return job

def run_enrichment(company: Company) -> Company:
    if company.website_url and not company.email:
        try:
            email = extract_email_from_company_page(company.website_url)
            if email:
                company.email = email
                company.save()
        except Exception as e:
            log.warning("enrichment failed for %s: %s", company.name, e)
    return company

def mark_run_complete(run: ScrapeRun, *, ok: bool, logs: str = "") -> None:
    run.status = "success" if ok else "failed"
    run.finished_at = timezone.now()
    if logs:
        run.logs = (run.logs or "") + "\n" + logs
    run.save()
