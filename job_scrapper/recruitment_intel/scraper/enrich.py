import re
from bs4 import BeautifulSoup
from typing import Tuple
import requests

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)

def extract_email_from_company_page(url: str) -> str:
    """Portfolio-safe enrichment: fetch a company page (file:// or http(s)://) and parse emails."""
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Prefer mailto links
    mailto = soup.select_one('a[href^="mailto:"]')
    if mailto and mailto.get("href"):
        return mailto["href"].replace("mailto:", "").strip()

    # Fallback: regex scan
    text = soup.get_text(" ", strip=True)
    m = EMAIL_RE.search(text)
    return m.group(0) if m else ""
