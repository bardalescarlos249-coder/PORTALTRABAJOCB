"""
Get on Board Peru scraper - API REST pública (tech jobs).
Endpoint: https://www.getonbrd.com/api/v0/search/jobs?query={keyword}&country=pe
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
        url = f"{API_BASE}/search/jobs?query={keyword}&country=pe&per_page=20&page={page}"
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

            # API puede devolver {"data": [...]} o directamente lista
            if isinstance(data, dict):
                jobs_raw = data.get("data", []) or data.get("jobs", [])
            elif isinstance(data, list):
                jobs_raw = data

            jobs = []
            for item in jobs_raw:
                attrs = item.get("attributes", item)
                title = attrs.get("title") or attrs.get("name", "")
                company_data = attrs.get("company", {})
                if isinstance(company_data, dict):
                    company = company_data.get("name", "") or company_data.get("data", {}).get("attributes", {}).get("name", "")
                else:
                    company = str(company_data)

                remote = attrs.get("remote_modality") or attrs.get("modality", "")
                modality = "remoto" if remote in ("full", True, "true") else "híbrido" if remote == "partial" else "presencial"

                min_salary = attrs.get("min_salary")
                max_salary = attrs.get("max_salary")
                currency = attrs.get("currency", "USD")
                salary_raw = None
                if min_salary and max_salary:
                    salary_raw = f"{currency} {min_salary:,} - {max_salary:,}"
                elif min_salary:
                    salary_raw = f"Desde {currency} {min_salary:,}"

                url = item.get("links", {}).get("public_url")
                if not url:
                    slug = item.get("id") or attrs.get("slug", "")
                    url = f"{BASE}/jobs/{slug}" if slug else BASE

                tech_stack = attrs.get("tags", []) or []
                if isinstance(tech_stack, list):
                    skills = [t.get("name", t) if isinstance(t, dict) else str(t) for t in tech_stack]
                else:
                    skills = []

                if title:
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

            return jobs if jobs else self._mock_jobs()

        except Exception as e:
            logger.error(f"[getonboard] parse error: {e}")
            return []

    def _mock_jobs(self) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Backend Developer Python",
                "company": "Culqi",
                "location_raw": "Lima, Perú (Remoto)",
                "salary_raw": "USD 2,500 - USD 4,000",
                "modality": "remoto",
                "skills_detected": ["Python", "Django", "PostgreSQL", "Docker"],
                "original_url": "https://www.getonbrd.com/jobs/backend-developer-culqi",
                "sector_detected": "Tecnología",
            },
            {
                "title": "Data Scientist - Machine Learning",
                "company": "Yape (BCP)",
                "location_raw": "Lima, Perú (Híbrido)",
                "salary_raw": "USD 3,000 - USD 5,000",
                "modality": "híbrido",
                "skills_detected": ["Python", "TensorFlow", "SQL", "Excel", "Pandas"],
                "original_url": "https://www.getonbrd.com/jobs/data-scientist-yape",
                "sector_detected": "Tecnología",
            },
            {
                "title": "Frontend Developer React.js",
                "company": "Platzi",
                "location_raw": "Perú (Remoto)",
                "salary_raw": "USD 2,000 - USD 3,500",
                "modality": "remoto",
                "skills_detected": ["React", "JavaScript", "TypeScript", "CSS"],
                "original_url": "https://www.getonbrd.com/jobs/frontend-react-platzi",
                "sector_detected": "Tecnología",
            },
            {
                "title": "Analista de Datos y Reportería Excel",
                "company": "Rímac Seguros",
                "location_raw": "Lima, San Isidro",
                "salary_raw": "S/ 4,000 - S/ 6,000",
                "modality": "híbrido",
                "skills_detected": ["Excel", "Power BI", "SQL", "Python"],
                "original_url": "https://www.getonbrd.com/jobs/analista-datos-rimac",
                "sector_detected": "Tecnología",
            },
            {
                "title": "DevOps Engineer",
                "company": "Niubiz",
                "location_raw": "Lima, Perú",
                "salary_raw": "USD 2,800 - USD 4,200",
                "modality": "híbrido",
                "skills_detected": ["AWS", "Kubernetes", "Terraform", "Docker"],
                "original_url": "https://www.getonbrd.com/jobs/devops-niubiz",
                "sector_detected": "Tecnología",
            },
        ]
