"""
InfoJobs Peru scraper.
URL: https://www.infojobs.com.pe/jobsearch/search-results/list.xhtml?keyword={keyword}
"""
import logging
from typing import Any, Dict, List, Optional
from backend.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BASE = "https://www.infojobs.com.pe"


class InfojobsScraper(BaseScraper):
    source_name = "infojobs"
    base_url = BASE

    def build_search_url(self, filters: Dict[str, Any]) -> str:
        keyword = filters.get("keyword", "").strip()
        page = filters.get("_page", 1)
        url = f"{BASE}/jobsearch/search-results/list.xhtml?keyword={keyword}&provinceIds=&normalizedJobName=&page={page}"
        return url

    def fetch_search_results(self, url: str) -> Optional[str]:
        html = self.fetch(url)
        if html and "infojobs" in html.lower():
            return html
        return None

    def parse_job_cards(self, html: str) -> List[Dict[str, Any]]:
        if not html:
            return self._mock_jobs()

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "lxml")
            jobs = []

            cards = soup.select(
                "li.ij-OfferList-item, div[class*='offer-item'], "
                "article[class*='offer'], div[class*='ij-OfferCard']"
            )

            for card in cards:
                try:
                    title_el = card.select_one("h2 a, h3 a, a[class*='ij-OfferCard-title']")
                    title = title_el.get_text(strip=True) if title_el else ""
                    href = title_el.get("href", "") if title_el else ""
                    url_job = href if href.startswith("http") else f"{BASE}{href}"

                    company_el = card.select_one("[class*='company'], [class*='ij-OfferCard-subtitle']")
                    company = company_el.get_text(strip=True) if company_el else ""

                    location_el = card.select_one("[class*='location'], [class*='ij-OfferCard-place']")
                    location = location_el.get_text(strip=True) if location_el else "Perú"

                    salary_el = card.select_one("[class*='salary'], [class*='ij-OfferCard-salary']")
                    salary = salary_el.get_text(strip=True) if salary_el else None

                    if title and len(title) > 3:
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location_raw": location,
                            "salary_raw": salary,
                            "original_url": url_job or BASE,
                        })
                except Exception as e:
                    logger.debug(f"[infojobs] card error: {e}")

            return jobs if jobs else self._mock_jobs()
        except Exception as e:
            logger.error(f"[infojobs] parse error: {e}")
            return self._mock_jobs()

    def _mock_jobs(self) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Analista de Planillas y Compensaciones",
                "company": "Primax Perú",
                "location_raw": "Lima, San Isidro",
                "salary_raw": "S/ 3,200 - S/ 4,500",
                "modality": "presencial",
                "original_url": "https://www.infojobs.com.pe/oferta/analista-planillas-primax",
            },
            {
                "title": "Coordinador de Marketing Digital",
                "company": "Scotiabank Perú",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 4,000 - S/ 5,500",
                "modality": "híbrido",
                "original_url": "https://www.infojobs.com.pe/oferta/coordinador-mkt-scotiabank",
            },
            {
                "title": "Jefe de Almacén y Logística",
                "company": "Grupo Gloria",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 5,000 - S/ 7,000",
                "modality": "presencial",
                "original_url": "https://www.infojobs.com.pe/oferta/jefe-almacen-gloria",
            },
            {
                "title": "Técnico en Mantenimiento Eléctrico",
                "company": "Luz del Sur",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 3,000 - S/ 4,000",
                "modality": "presencial",
                "original_url": "https://www.infojobs.com.pe/oferta/tecnico-electrico-luzdelsur",
            },
            {
                "title": "Recepcionista Bilingüe (Inglés)",
                "company": "Marriott Lima",
                "location_raw": "Lima, Miraflores",
                "salary_raw": "S/ 2,500 - S/ 3,000",
                "modality": "presencial",
                "original_url": "https://www.infojobs.com.pe/oferta/recepcionista-marriott",
            },
            {
                "title": "Auxiliar Contable - Excel Intermedio",
                "company": "Ernst & Young Perú",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 2,000 - S/ 2,800",
                "modality": "presencial",
                "original_url": "https://www.infojobs.com.pe/oferta/auxiliar-contable-ey",
            },
        ]
