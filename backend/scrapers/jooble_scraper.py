"""
Jooble Peru scraper - JSON API oficial con clave pública.
Docs: https://jooble.org/api/about
"""
import logging
import json
from typing import Any, Dict, List, Optional
from backend.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BASE = "https://pe.jooble.org"
# Jooble tiene una API pública. El key '0' es el endpoint de demo/público.
JOOBLE_API = "https://jooble.org/api/0"


class JoobleScraper(BaseScraper):
    source_name = "jooble"
    base_url = BASE

    def build_search_url(self, filters: Dict[str, Any]) -> str:
        # Jooble usa POST, devolvemos la URL del endpoint
        self._filters = filters
        return JOOBLE_API

    def fetch_search_results(self, url: str) -> Optional[str]:
        try:
            keyword = self._filters.get("keyword", "")
            payload = json.dumps({"keywords": keyword, "location": "Perú", "page": "1"})
            self.session.headers.update({
                "Content-Type": "application/json",
                "Accept": "application/json",
            })
            response = self.session.post(url, data=payload, timeout=20)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            logger.warning(f"[jooble] API error: {e}")
        return None

    def parse_job_cards(self, html: str) -> List[Dict[str, Any]]:
        if not html:
            return []
        try:
            data = json.loads(html)
            items = data.get("jobs", [])
            jobs = []
            for item in items:
                title = item.get("title", "")
                company = item.get("company", "")
                location = item.get("location", "Perú")
                salary = item.get("salary", None)
                url = item.get("link", BASE)
                if title and len(title) > 3:
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location_raw": location,
                        "salary_raw": salary,
                        "original_url": url,
                    })
            return jobs
        except Exception as e:
            logger.error(f"[jooble] parse error: {e}")
            return []
