"""
Bumeran Peru scraper - API REST interna.
"""
import logging
import json
from typing import Any, Dict, List, Optional
from backend.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BASE = "https://www.bumeran.com.pe"
API = "https://api.bumeran.com.pe/api/v1"


class BumeranScraper(BaseScraper):
    source_name = "bumeran"
    base_url = BASE

    def build_search_url(self, filters: Dict[str, Any]) -> str:
        keyword = filters.get("keyword", "").strip()
        page = filters.get("_page", 1)
        self.session.headers.update({
            "Accept": "application/json",
            "Referer": "https://www.bumeran.com.pe/",
        })
        url = f"{API}/postulations/search?keywords={keyword}&page={page}&pagesize=20&country=PE"
        return url

    def fetch_search_results(self, url: str) -> Optional[str]:
        try:
            html = self.fetch(url)
            if html and ("results" in html or "postulations" in html):
                return html
        except Exception as e:
            logger.warning(f"[bumeran] API error: {e}")
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
                if isinstance(company, dict):
                    company_name = company.get("name", "")
                else:
                    company_name = str(company)
                location = item.get("zone", {})
                if isinstance(location, dict):
                    location_str = location.get("description", "Perú")
                else:
                    location_str = "Perú"
                salary = item.get("salary", {})
                if isinstance(salary, dict):
                    salary_str = salary.get("description")
                else:
                    salary_str = None
                job_id = item.get("id", "")
                url = item.get("url") or (f"{BASE}/empleos/oferta-de-trabajo-{job_id}.html" if job_id else BASE)
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
            logger.error(f"[bumeran] parse error: {e}")
            return []
