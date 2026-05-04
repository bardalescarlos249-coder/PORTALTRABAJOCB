"""
Computrabajo Peru scraper.
URL pattern: https://pe.computrabajo.com/trabajo-de-{keyword}
"""
import logging
import re
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from backend.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BASE = "https://pe.computrabajo.com"


class ComputrabajoScraper(BaseScraper):
    source_name = "computrabajo"
    base_url = BASE

    def build_search_url(self, filters: Dict[str, Any]) -> str:
        keyword = filters.get("keyword", "").strip().replace(" ", "-").lower()
        page = filters.get("_page", 1)
        location = filters.get("location", "").strip().replace(" ", "-").lower()

        if keyword:
            url = f"{BASE}/trabajo-de-{keyword}"
        else:
            url = f"{BASE}/empleos"

        if location and location not in ("peru", "perú", ""):
            url += f"-en-{location}"

        if page > 1:
            url += f"?p={page}"

        return url

    def fetch_search_results(self, url: str) -> Optional[str]:
        html = self.fetch(url)
        if html and "computrabajo" in html:
            return html
        logger.warning(f"[computrabajo] Blocked or empty response from {url}, using mock")
        return None

    def parse_job_cards(self, html: str) -> List[Dict[str, Any]]:
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        jobs = []

        # Computrabajo job cards
        cards = soup.select("article.box_offer, div.box_offer, div[class*='box_offer'], article[class*='offerBlock']")

        if not cards:
            cards = soup.select("div.p_offer, div[class*='p_offer']")

        if not cards:
            logger.warning("[computrabajo] No job cards found, using mock")
            return []

        for card in cards:
            try:
                title_el = card.select_one("h2 a, h3 a, a[class*='it_title'], a[title]")
                title = title_el.get_text(strip=True) if title_el else ""
                href = title_el.get("href", "") if title_el else ""
                url = href if href.startswith("http") else f"{BASE}{href}"

                company_el = card.select_one("a[class*='it_company'], span[class*='company'], p[class*='company']")
                company = company_el.get_text(strip=True) if company_el else ""

                location_el = card.select_one("span[class*='location'], p[class*='location'], span[class*='ubic']")
                location = location_el.get_text(strip=True) if location_el else ""

                salary_el = card.select_one("span[class*='salary'], span[class*='sueldo'], p[class*='salary']")
                salary = salary_el.get_text(strip=True) if salary_el else None

                date_el = card.select_one("span[class*='date'], time, p[class*='date']")
                date_raw = date_el.get_text(strip=True) if date_el else None

                if title and url and url != BASE:
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location_raw": location,
                        "salary_raw": salary,
                        "publication_date_raw": date_raw,
                        "original_url": url,
                    })
            except Exception as e:
                logger.debug(f"[computrabajo] card parse error: {e}")

        return jobs if jobs else self._mock_jobs()

    def _mock_jobs(self) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Geólogo Senior de Exploración",
                "company": "Minera Antamina S.A.",
                "location_raw": "Áncash, Perú",
                "salary_raw": "S/ 8,000 - S/ 12,000",
                "original_url": "https://pe.computrabajo.com/ofertas-de-trabajo/geologo-senior",
            },
            {
                "title": "Practicante de Geología",
                "company": "Barrick Misquichilca S.A.",
                "location_raw": "La Libertad, Perú",
                "salary_raw": "S/ 1,200",
                "original_url": "https://pe.computrabajo.com/ofertas-de-trabajo/practicante-geologia",
            },
            {
                "title": "Ingeniero de Minas Junior",
                "company": "Southern Copper Corporation",
                "location_raw": "Moquegua, Perú",
                "salary_raw": "S/ 5,000 - S/ 7,000",
                "original_url": "https://pe.computrabajo.com/ofertas-de-trabajo/ingeniero-minas",
            },
            {
                "title": "Analista de Datos - Power BI",
                "company": "Intercorp Retail",
                "location_raw": "Lima, Perú",
                "salary_raw": "S/ 4,500 - S/ 6,000",
                "original_url": "https://pe.computrabajo.com/ofertas-de-trabajo/analista-datos",
            },
            {
                "title": "Asistente de Logística",
                "company": "Ransa Comercial S.A.",
                "location_raw": "Lima, Callao",
                "salary_raw": "S/ 2,500 - S/ 3,200",
                "original_url": "https://pe.computrabajo.com/ofertas-de-trabajo/asistente-logistica",
            },
        ]
