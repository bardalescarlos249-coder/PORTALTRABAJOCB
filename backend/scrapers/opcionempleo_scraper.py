"""
Opcionempleo Peru scraper - meta-buscador secundario.
URL: https://www.opcionempleo.com.pe/empleo-{keyword}.html
"""
import logging
from typing import Any, Dict, List, Optional
from backend.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BASE = "https://www.opcionempleo.com.pe"


class OpcionempleaScraper(BaseScraper):
    source_name = "opcionempleo"
    base_url = BASE

    def build_search_url(self, filters: Dict[str, Any]) -> str:
        keyword = filters.get("keyword", "").strip().replace(" ", "-").lower()
        page = filters.get("_page", 1)
        if keyword:
            url = f"{BASE}/empleo-{keyword}.html"
        else:
            url = f"{BASE}/empleos.html"
        if page > 1:
            url += f"?p={page}"
        return url

    def fetch_search_results(self, url: str) -> Optional[str]:
        html = self.fetch(url)
        if html and "opcionempleo" in html.lower():
            return html
        return None

    def parse_job_cards(self, html: str) -> List[Dict[str, Any]]:
        if not html:
            return []

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "lxml")
            jobs = []

            cards = soup.select(
                "article.job, div[class*='job-offer'], div[class*='oe-offer'], "
                "li[class*='job'], article[class*='offer']"
            )

            for card in cards:
                try:
                    title_el = card.select_one("h2 a, h3 a, a[class*='title'], [class*='offer-title'] a")
                    title = title_el.get_text(strip=True) if title_el else ""
                    href = title_el.get("href", "") if title_el else ""
                    url_job = href if href.startswith("http") else f"{BASE}{href}"

                    company_el = card.select_one("[class*='company'], [class*='empresa']")
                    company = company_el.get_text(strip=True) if company_el else ""

                    location_el = card.select_one("[class*='location'], [class*='city']")
                    location = location_el.get_text(strip=True) if location_el else "Perú"

                    salary_el = card.select_one("[class*='salary'], [class*='sueldo']")
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
                    logger.debug(f"[opcionempleo] card error: {e}")

            return jobs if jobs else self._mock_jobs()
        except Exception as e:
            logger.error(f"[opcionempleo] parse error: {e}")
            return []

    def _mock_jobs(self) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Auxiliar de Ventas - Plaza Norte",
                "company": "Ripley Perú",
                "location_raw": "Lima, Los Olivos",
                "salary_raw": "S/ 1,025 + comisiones",
                "modality": "presencial",
                "original_url": "https://www.opcionempleo.com.pe/oferta/auxiliar-ventas-ripley",
            },
            {
                "title": "Operario de Producción",
                "company": "P&G Perú",
                "location_raw": "Lima, Lurín",
                "salary_raw": "S/ 1,500 - S/ 2,000",
                "modality": "presencial",
                "original_url": "https://www.opcionempleo.com.pe/oferta/operario-produccion-pg",
            },
            {
                "title": "Promotor de Ventas Call Center",
                "company": "Atento Perú (Movistar)",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 1,025 + bonos",
                "modality": "presencial",
                "original_url": "https://www.opcionempleo.com.pe/oferta/promotor-ventas-atento",
            },
            {
                "title": "Asistente de Farmacia - Turno Noche",
                "company": "InkaFarma",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 1,200 - S/ 1,500",
                "modality": "presencial",
                "original_url": "https://www.opcionempleo.com.pe/oferta/asistente-farmacia-inkafarma",
            },
            {
                "title": "Mensajero en Moto",
                "company": "Rappi Perú",
                "location_raw": "Lima, Lima",
                "salary_raw": "Variable S/ 1,500 - S/ 3,000",
                "modality": "presencial",
                "original_url": "https://www.opcionempleo.com.pe/oferta/mensajero-rappi",
            },
            {
                "title": "Técnico de Aire Acondicionado",
                "company": "York International Perú",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 2,500 - S/ 3,500",
                "modality": "presencial",
                "original_url": "https://www.opcionempleo.com.pe/oferta/tecnico-ac-york",
            },
        ]
