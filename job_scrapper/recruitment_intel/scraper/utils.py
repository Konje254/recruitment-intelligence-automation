import logging
import re
import time
from dataclasses import dataclass
from typing import Callable, Optional, TypeVar

T = TypeVar("T")
log = logging.getLogger("scraper")

def normalize_text(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^a-z0-9\s\-]", "", s)
    return s.strip()

def make_job_key(title: str, company: str, location: str) -> str:
    return "|".join([normalize_text(title), normalize_text(company), normalize_text(location)])

def retry(fn: Callable[[], T], *, tries: int = 3, delay: float = 0.8, backoff: float = 1.7, exc: tuple = (Exception,)) -> T:
    last_err: Optional[Exception] = None
    for i in range(tries):
        try:
            return fn()
        except exc as e:
            last_err = e
            sleep_for = delay * (backoff ** i)
            log.warning("retry %s/%s after error: %s (sleep %.2fs)", i + 1, tries, e, sleep_for)
            time.sleep(sleep_for)
    raise last_err  # type: ignore
