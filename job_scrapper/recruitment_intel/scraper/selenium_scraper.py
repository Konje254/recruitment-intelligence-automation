import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .utils import retry

log = logging.getLogger("scraper")

@dataclass
class ScrapedJob:
    title: str
    location: str
    company: str
    description: str
    source_url: str
    company_site: str

class FixtureScraper:
    """Scrape local HTML fixtures using Selenium (portfolio-safe)."""

    def __init__(self, *, headless: bool = True, timeout: int = 10):
        self.timeout = timeout
        opts = Options()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=opts)

    def close(self):
        self.driver.quit()

    def _wait(self):
        return WebDriverWait(self.driver, self.timeout)

    def scrape_platform(self, fixtures_root: Path, platform: str, limit: int = 50) -> List[ScrapedJob]:
        start = fixtures_root / platform / "listings_1.html"
        start_url = start.resolve().as_uri()

        jobs: List[ScrapedJob] = []
        self.driver.get(start_url)

        while len(jobs) < limit:
            self._wait().until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-test="job-card"]')))
            cards = self.driver.find_elements(By.CSS_SELECTOR, '[data-test="job-card"]')

            for card in cards:
                if len(jobs) >= limit:
                    break
                link = card.find_element(By.CSS_SELECTOR, '[data-test="job-link"]')
                href = link.get_attribute("href")
                job = retry(lambda: self._scrape_detail(href), tries=3)
                jobs.append(job)

            # Next page?
            next_links = self.driver.find_elements(By.CSS_SELECTOR, '[data-test="next-page"]')
            if next_links and len(jobs) < limit:
                next_links[0].click()
            else:
                break

        return jobs

    def _scrape_detail(self, url: str) -> ScrapedJob:
        self.driver.get(url)
        self._wait().until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="job-title"]')))

        title = self.driver.find_element(By.CSS_SELECTOR, '[data-test="job-title"]').text.strip()
        company = self.driver.find_element(By.CSS_SELECTOR, '[data-test="company-name"]').text.strip()
        location = self.driver.find_element(By.CSS_SELECTOR, '[data-test="job-location"]').text.strip()
        description = self.driver.find_element(By.CSS_SELECTOR, '[data-test="job-description"]').text.strip()
        company_site = self.driver.find_element(By.CSS_SELECTOR, '[data-test="company-site"]').get_attribute("href")

        return ScrapedJob(
            title=title,
            location=location,
            company=company,
            description=description,
            source_url=url,
            company_site=company_site,
        )
