"""
Laborum Peru scraper - API REST interna v2.
"""
import logging
import json
from typing import Any, Dict, List, Optional
from backend.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BASE = "https://www.laborum.pe"
API = "https://api.laborum.pe/api/v1"


class LaborumScraper(BaseScraper):
    source_name = "laborum"
    base_url = BASE

    def build_search_url(self, filters: Dict[str, Any]) -> str:
        keyword = filters.get("keyword", "").strip()
        page = filters.get("_page", 1)
        self.session.headers.update({
            "Accept": "application/json",
            "Referer": "https://www.laborum.pe/",
        })
        url = f"{API}/postulations/search?keywords={keyword}&page={page}&pagesize=20&country=PE"
        return url

    def fetch_search_results(self, url: str) -> Optional[str]:
        try:
            html = self.fetch(url)
            if html and ("results" in html or "postulations" in html):
                return html
        except Exception as e:
            logger.warning(f"[laborum] API error: {e}")
        return None

    def parse_job_cards(self, html: str) -> List[Dict[str, Any]]:
        if not html:
            return []
        try:
            data = json.loads(html)
            items = data.get("results", data.get("postulations", []))
            if not isinstance(items, list):
                return []
            jobs = []
            for item in items:
                title = item.get("title") or item.get("name", "")
                company = item.get("company", {})
                company_name = company.get("name", "") if isinstance(company, dict) else str(company)
                location = item.get("zone", {})
                location_str = location.get("description", "Perú") if isinstance(location, dict) else "Perú"
                salary = item.get("salary", {})
                salary_str = salary.get("description") if isinstance(salary, dict) else None
                job_id = item.get("id", "")
                url = item.get("url") or (f"{BASE}/empleos/oferta-{job_id}.html" if job_id else BASE)
                if title:
                    jobs.append({
                        "title": title,
                        "company": company_name,
                        "location_raw": location_str,
                        "salary_raw": salary_str,
                        "original_url": url,
                    })
            return jobs
        except Exception as e:
            logger.error(f"[laborum] parse error: {e}")
            return []
