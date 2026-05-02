"""
Base scraper abstract class.
"""
import random
import time
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
from sqlalchemy.orm import Session

from backend.models import Job
from backend.normalizer.normalizer import normalize_job

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


class BaseScraper(ABC):
    source_name: str = "unknown"
    base_url: str = ""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def delay(self, min_s: float = 1.5, max_s: float = 4.0):
        time.sleep(random.uniform(min_s, max_s))

    def fetch(self, url: str, timeout: int = 15) -> Optional[str]:
        try:
            resp = self.session.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            logger.warning(f"[{self.source_name}] Error fetching {url}: {e}")
            return None

    @abstractmethod
    def build_search_url(self, filters: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def fetch_search_results(self, url: str) -> Optional[str]:
        pass

    @abstractmethod
    def parse_job_cards(self, html: str) -> List[Dict[str, Any]]:
        pass

    def normalize_job_data(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        return normalize_job(raw, self.source_name)

    def run(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        max_pages = filters.get("max_pages", 2)

        for page in range(1, max_pages + 1):
            filters["_page"] = page
            url = self.build_search_url(filters)
            logger.info(f"[{self.source_name}] Scraping page {page}: {url}")

            html = self.fetch_search_results(url)
            if not html:
                logger.warning(f"[{self.source_name}] No HTML on page {page}, stopping.")
                break

            cards = self.parse_job_cards(html)
            if not cards:
                logger.info(f"[{self.source_name}] No cards on page {page}, stopping.")
                break

            for card in cards:
                normalized = self.normalize_job_data(card)
                if normalized.get("title") and normalized.get("original_url"):
                    results.append(normalized)

            self.delay()

        logger.info(f"[{self.source_name}] Total scraped: {len(results)}")
        return results

    def save_results(self, jobs: List[Dict[str, Any]], db: Session):
        saved = 0
        for job_data in jobs:
            url = job_data.get("original_url", "")
            if not url:
                continue
            existing = db.query(Job).filter(Job.original_url == url).first()
            if existing:
                continue
            try:
                job = Job(**{k: v for k, v in job_data.items() if hasattr(Job, k)})
                job.scraped_at = datetime.utcnow()
                db.add(job)
                saved += 1
            except Exception as e:
                logger.error(f"[{self.source_name}] Error saving job: {e}")
        db.commit()
        logger.info(f"[{self.source_name}] Saved {saved} new jobs.")
        return saved
