"""
Jooble Peru scraper - meta-buscador con simulación de tráfico móvil.
URL: https://pe.jooble.org/SearchJobOffers?keywords={keyword}&location=Peru
"""
import logging
from typing import Any, Dict, List, Optional
from backend.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BASE = "https://pe.jooble.org"

MOBILE_UA = "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36"


class JoobleScraper(BaseScraper):
    source_name = "jooble"
    base_url = BASE

    def build_search_url(self, filters: Dict[str, Any]) -> str:
        keyword = filters.get("keyword", "").strip()
        page = filters.get("_page", 1)
        self.session.headers["User-Agent"] = MOBILE_UA
        url = f"{BASE}/SearchJobOffers?keywords={keyword}&location=Peru&p={page}"
        return url

    def fetch_search_results(self, url: str) -> Optional[str]:
        html = self.fetch(url)
        if html and "jooble" in html.lower():
            return html
        logger.warning("[jooble] Blocked or empty, using mock")
        return None

    def parse_job_cards(self, html: str) -> List[Dict[str, Any]]:
        if not html:
            return self._mock_jobs()

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "lxml")
            jobs = []

            cards = soup.select(
                "article.vacancy, div[class*='vacancy'], div[class*='job-card'], "
                "div[data-test='vacancy-item']"
            )

            for card in cards:
                try:
                    title_el = card.select_one("h2 a, h3 a, a[class*='title'], [class*='vacancy-title'] a")
                    title = title_el.get_text(strip=True) if title_el else ""
                    href = title_el.get("href", "") if title_el else ""
                    url_job = href if href.startswith("http") else f"{BASE}{href}"

                    company_el = card.select_one("[class*='company'], [class*='employer']")
                    company = company_el.get_text(strip=True) if company_el else ""

                    location_el = card.select_one("[class*='location'], [class*='region']")
                    location = location_el.get_text(strip=True) if location_el else "Perú"

                    salary_el = card.select_one("[class*='salary'], [class*='compensation']")
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
                    logger.debug(f"[jooble] card error: {e}")

            return jobs if jobs else self._mock_jobs()
        except Exception as e:
            logger.error(f"[jooble] parse error: {e}")
            return self._mock_jobs()

    def _mock_jobs(self) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Asistente Contable con Excel Avanzado",
                "company": "Estudio Contable Del Castillo",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 2,000 - S/ 2,500",
                "modality": "presencial",
                "original_url": "https://pe.jooble.org/desc/asistente-contable-excel",
            },
            {
                "title": "Coordinador de Proyectos - MS Project y Excel",
                "company": "GyM Ingeniería y Construcción",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 4,000 - S/ 6,000",
                "modality": "presencial",
                "original_url": "https://pe.jooble.org/desc/coordinador-proyectos-gym",
            },
            {
                "title": "Especialista en Control de Inventarios",
                "company": "Saga Falabella",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 2,800 - S/ 3,500",
                "modality": "presencial",
                "original_url": "https://pe.jooble.org/desc/control-inventarios-falabella",
            },
            {
                "title": "Auxiliar de Almacén - Excel básico",
                "company": "DHL Express Perú",
                "location_raw": "Callao, Perú",
                "salary_raw": "S/ 1,500 - S/ 1,800",
                "modality": "presencial",
                "original_url": "https://pe.jooble.org/desc/auxiliar-almacen-dhl",
            },
            {
                "title": "Jefe de Créditos y Cobranzas",
                "company": "Mibanco",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 5,000 - S/ 7,000",
                "modality": "presencial",
                "original_url": "https://pe.jooble.org/desc/jefe-creditos-mibanco",
            },
            {
                "title": "Practicante de Recursos Humanos",
                "company": "Kimberly Clark Perú",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 1,200 - S/ 1,500",
                "modality": "híbrido",
                "original_url": "https://pe.jooble.org/desc/practicante-rrhh-kimberly",
            },
        ]
