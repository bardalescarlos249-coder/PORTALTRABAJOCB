"""
GetOnBoard Peru scraper - API REST pública (tech jobs).
Endpoint: https://www.getonbrd.com/api/v0/search/jobs?query={keyword}&country=pe
IMPORTANTE: La API devuelve URLs directas válidas en links.public_url.
"""
import logging
import json
from typing import Any, Dict, List, Optional
from backend.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BASE = "https://www.getonbrd.com"
API_BASE = "https://www.getonbrd.com/api/v0"


class GetonboardScraper(BaseScraper):
    source_name = "getonboard"
    base_url = BASE

    def build_search_url(self, filters: Dict[str, Any]) -> str:
        keyword = filters.get("keyword", "").strip()
        page = filters.get("_page", 1)
        # Include expand=company,tags to get full URLs
        url = f"{API_BASE}/search/jobs?query={keyword}&country=pe&per_page=20&page={page}&expand=company,tags"
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        return url

    def fetch_search_results(self, url: str) -> Optional[str]:
        try:
            html = self.fetch(url)
            if html and ("data" in html or "jobs" in html.lower()):
                return html
        except Exception as e:
            logger.warning(f"[getonboard] API error: {e}")
        return None

    def parse_job_cards(self, html: str) -> List[Dict[str, Any]]:
        if not html:
            return []

        try:
            data = json.loads(html)
            jobs_raw = []

            if isinstance(data, dict):
                jobs_raw = data.get("data", []) or data.get("jobs", [])
            elif isinstance(data, list):
                jobs_raw = data

            jobs = []
            for item in jobs_raw:
                attrs = item.get("attributes", item)
                title = attrs.get("title") or attrs.get("name", "")
                if not title:
                    continue

                # Company name
                company_data = attrs.get("company", {})
                if isinstance(company_data, dict):
                    # Try nested attributes first (expanded response)
                    nested = company_data.get("data", {})
                    if isinstance(nested, dict):
                        company = nested.get("attributes", {}).get("name", "")
                    else:
                        company = company_data.get("name", "")
                else:
                    company = str(company_data)

                # Modality
                remote = attrs.get("remote_modality") or attrs.get("modality", "")
                if remote in ("full", True, "true"):
                    modality = "remoto"
                elif remote == "partial":
                    modality = "híbrido"
                else:
                    modality = "presencial"

                # Salary
                min_salary = attrs.get("min_salary")
                max_salary = attrs.get("max_salary")
                currency = attrs.get("currency", "USD")
                salary_raw = None
                if min_salary and max_salary:
                    salary_raw = f"{currency} {min_salary:,} - {max_salary:,}"
                elif min_salary:
                    salary_raw = f"Desde {currency} {min_salary:,}"

                # URL - CRITICAL: use public_url from links, fallback to web_url
                links = item.get("links", {})
                url = (
                    links.get("public_url")
                    or links.get("web_url")
                    or attrs.get("public_url")
                    or attrs.get("url")
                )
                # If still no URL, try to build from company slug + job slug
                if not url:
                    company_slug = ""
                    if isinstance(company_data, dict):
                        nested_attrs = company_data.get("data", {}).get("attributes", {})
                        company_slug = nested_attrs.get("slug", "")
                    job_slug = attrs.get("slug", "")
                    if company_slug and job_slug:
                        url = f"{BASE}/{company_slug}/jobs/{job_slug}"
                    else:
                        # Last resort: link to getonboard search, not a broken detail page
                        url = f"{BASE}/jobs"

                # Skills/tags
                tech_stack = attrs.get("tags", []) or []
                if isinstance(tech_stack, list):
                    skills = [t.get("name", t) if isinstance(t, dict) else str(t) for t in tech_stack]
                else:
                    skills = []

                jobs.append({
                    "title": title,
                    "company": company,
                    "location_raw": "Perú (Remoto)" if modality == "remoto" else "Lima, Perú",
                    "salary_raw": salary_raw,
                    "modality": modality,
                    "skills_detected": skills,
                    "original_url": url,
                    "sector_detected": "Tecnología",
                })

            return jobs

        except Exception as e:
            logger.error(f"[getonboard] parse error: {e}")
            return []
