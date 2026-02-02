import logging
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from scraper.models import Platform, ScrapeRun
from scraper.selenium_scraper import FixtureScraper
from scraper.services import upsert_company, upsert_job, mark_run_complete, run_enrichment

log = logging.getLogger("scraper")

class Command(BaseCommand):
    help = "Scrape local HTML fixtures with Selenium and store results in Django models."

    def add_arguments(self, parser):
        parser.add_argument("--platform", required=True, choices=["indeed", "glassdoor", "linkedin"])
        parser.add_argument("--limit", type=int, default=25)
        parser.add_argument("--headless", action="store_true", default=True)

    def handle(self, *args, **opts):
        logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

        platform = Platform.objects.get(name=opts["platform"])
        limit = int(opts["limit"])
        run = ScrapeRun.objects.create(platform=platform, requested_limit=limit)

        fixtures_root = Path(__file__).resolve().parents[4] / "demo_pages"
        scraper = FixtureScraper(headless=opts["headless"])

        ok = True
        try:
            scraped = scraper.scrape_platform(fixtures_root, platform.name, limit=limit)
            for item in scraped:
                company = upsert_company(item.company, website_url=item.company_site)
                company = run_enrichment(company)
                upsert_job(
                    platform=platform,
                    title=item.title,
                    company=company,
                    location=item.location,
                    description=item.description,
                    source_url=item.source_url,
                )
        except Exception as e:
            ok = False
            log.exception("scrape failed: %s", e)
            mark_run_complete(run, ok=False, logs=str(e))
        finally:
            scraper.close()

        if ok:
            mark_run_complete(run, ok=True)
            self.stdout.write(self.style.SUCCESS(f"Scrape completed: {platform.name} (limit={limit})"))
