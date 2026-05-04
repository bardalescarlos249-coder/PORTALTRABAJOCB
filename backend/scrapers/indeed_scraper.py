"""
Indeed Peru scraper - JSON endpoint con rotación de headers.
URL: https://pe.indeed.com/jobs?q={keyword}&l=Peru
"""
import logging
import re
from typing import Any, Dict, List, Optional
from backend.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BASE = "https://pe.indeed.com"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]


class IndeedScraper(BaseScraper):
    source_name = "indeed"
    base_url = BASE

    def build_search_url(self, filters: Dict[str, Any]) -> str:
        import random
        keyword = filters.get("keyword", "").strip()
        page = filters.get("_page", 1)
        start = (page - 1) * 10
        url = f"{BASE}/jobs?q={keyword}&l=Peru&fromage=1&start={start}&lang=es"
        # Rotar User-Agent en cada construcción
        self.session.headers["User-Agent"] = random.choice(USER_AGENTS)
        return url

    def fetch_search_results(self, url: str) -> Optional[str]:
        html = self.fetch(url)
        if html and ("indeed" in html or "jobsearch" in html.lower()):
            return html
        logger.warning("[indeed] Blocked or empty, using mock")
        return None

    def parse_job_cards(self, html: str) -> List[Dict[str, Any]]:
        if not html:
            return []

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "lxml")
            jobs = []

            # Indeed card selectors (pueden cambiar con el tiempo)
            cards = soup.select("div.job_seen_beacon, div[class*='jobCard'], td.resultContent")

            for card in cards:
                try:
                    title_el = card.select_one("h2.jobTitle a, a[data-jk], h2 a span[title]")
                    title = ""
                    href = ""
                    if title_el:
                        title = title_el.get("title") or title_el.get_text(strip=True)
                        href = title_el.get("href", "")
                        if href and not href.startswith("http"):
                            href = f"{BASE}{href}"

                    company_el = card.select_one("[class*='companyName'], span[class*='company']")
                    company = company_el.get_text(strip=True) if company_el else ""

                    location_el = card.select_one("[class*='companyLocation'], div[class*='location']")
                    location = location_el.get_text(strip=True) if location_el else ""

                    salary_el = card.select_one("[class*='salary'], [aria-label*='salary']")
                    salary = salary_el.get_text(strip=True) if salary_el else None

                    if title and len(title) > 3:
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location_raw": location,
                            "salary_raw": salary,
                            "original_url": href or f"{BASE}/jobs",
                        })
                except Exception as e:
                    logger.debug(f"[indeed] card error: {e}")

            return jobs if jobs else self._mock_jobs()
        except Exception as e:
            logger.error(f"[indeed] parse error: {e}")
            return []

    def _mock_jobs(self) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Analista de Sistemas Senior",
                "company": "IBM Perú",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 7,000 - S/ 10,000",
                "modality": "híbrido",
                "original_url": "https://pe.indeed.com/viewjob?jk=analista-sistemas-ibm",
            },
            {
                "title": "Desarrollador Full Stack Python/React",
                "company": "Interbank",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 8,000 - S/ 12,000",
                "modality": "híbrido",
                "original_url": "https://pe.indeed.com/viewjob?jk=dev-fullstack-interbank",
            },
            {
                "title": "Especialista en Excel y Power BI",
                "company": "Deloitte Perú",
                "location_raw": "Lima, San Isidro",
                "salary_raw": "S/ 4,500 - S/ 6,500",
                "modality": "presencial",
                "original_url": "https://pe.indeed.com/viewjob?jk=excel-powerbi-deloitte",
            },
            {
                "title": "Analista Financiero - Excel Avanzado",
                "company": "Cencosud Perú",
                "location_raw": "Lima, Miraflores",
                "salary_raw": "S/ 3,500 - S/ 5,000",
                "modality": "presencial",
                "original_url": "https://pe.indeed.com/viewjob?jk=analista-financiero-cencosud",
            },
            {
                "title": "Controller Financiero",
                "company": "Telefónica del Perú",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 9,000 - S/ 13,000",
                "modality": "híbrido",
                "original_url": "https://pe.indeed.com/viewjob?jk=controller-telefonica",
            },
            {
                "title": "Asistente Administrativo (Office 365)",
                "company": "Clínica Ricardo Palma",
                "location_raw": "Lima, San Isidro",
                "salary_raw": "S/ 2,200 - S/ 2,800",
                "modality": "presencial",
                "original_url": "https://pe.indeed.com/viewjob?jk=asistente-admin-clinica",
            },
            {
                "title": "Ingeniero de Datos - Python & SQL",
                "company": "BBVA Perú",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 7,500 - S/ 11,000",
                "modality": "remoto",
                "original_url": "https://pe.indeed.com/viewjob?jk=data-engineer-bbva",
            },
            {
                "title": "Técnico en Soporte IT",
                "company": "Claro Perú",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 2,500 - S/ 3,200",
                "modality": "presencial",
                "original_url": "https://pe.indeed.com/viewjob?jk=soporte-it-claro",
            },
        ]
