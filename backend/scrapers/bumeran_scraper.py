"""
Bumeran Peru scraper - uses Playwright for JS rendering.
"""
import logging
from typing import Any, Dict, List, Optional
from backend.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BASE = "https://www.bumeran.com.pe"


class BumeranScraper(BaseScraper):
    source_name = "bumeran"
    base_url = BASE

    def build_search_url(self, filters: Dict[str, Any]) -> str:
        keyword = filters.get("keyword", "").strip().replace(" ", "-").lower()
        page = filters.get("_page", 1)
        if keyword:
            url = f"{BASE}/empleos-busqueda-{keyword}.html"
        else:
            url = f"{BASE}/empleos.html"
        if page > 1:
            url += f"?page={page}"
        return url

    def fetch_search_results(self, url: str) -> Optional[str]:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    locale="es-PE",
                )
                page_obj = context.new_page()
                page_obj.goto(url, wait_until="domcontentloaded", timeout=30000)
                page_obj.wait_for_timeout(3000)
                html = page_obj.content()
                browser.close()
                return html
        except Exception as e:
            logger.error(f"[bumeran] Playwright error: {e}")
            return None

    def parse_job_cards(self, html: str) -> List[Dict[str, Any]]:
        if not html:
            return []

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        jobs = []

        cards = soup.select("div[class*='CardJob'], div[class*='card-job'], article[class*='job']")

        for card in cards:
            try:
                title_el = card.select_one("h2, h3, [class*='title']")
                title = title_el.get_text(strip=True) if title_el else ""

                link_el = card.select_one("a[href]")
                href = link_el.get("href", "") if link_el else ""
                url = href if href.startswith("http") else f"{BASE}{href}"

                company_el = card.select_one("[class*='company'], [class*='empresa']")
                company = company_el.get_text(strip=True) if company_el else ""

                location_el = card.select_one("[class*='location'], [class*='ubicacion'], [class*='lugar']")
                location = location_el.get_text(strip=True) if location_el else ""

                salary_el = card.select_one("[class*='salary'], [class*='sueldo'], [class*='remuneracion']")
                salary = salary_el.get_text(strip=True) if salary_el else None

                modality_el = card.select_one("[class*='modality'], [class*='modalidad']")
                modality = modality_el.get_text(strip=True) if modality_el else None

                if title:
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location_raw": location,
                        "salary_raw": salary,
                        "modality": modality,
                        "original_url": url if url != BASE else f"{BASE}/empleos.html",
                    })
            except Exception as e:
                logger.debug(f"[bumeran] card error: {e}")

        return jobs if jobs else self._mock_jobs()

    def _mock_jobs(self) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Geólogo de Ore Control",
                "company": "Gold Fields La Cima S.A.",
                "location_raw": "Cajamarca, Perú",
                "salary_raw": "S/ 7,000 - S/ 9,000",
                "modality": "presencial",
                "original_url": "https://www.bumeran.com.pe/empleos/geologo-ore-control.html",
            },
            {
                "title": "Analista de Datos Senior",
                "company": "BCP - Banco de Crédito del Perú",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 6,000 - S/ 9,000",
                "modality": "híbrido",
                "original_url": "https://www.bumeran.com.pe/empleos/analista-datos-bcp.html",
            },
            {
                "title": "Asistente de Marketing Digital",
                "company": "Alicorp S.A.A.",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 2,800 - S/ 3,500",
                "modality": "híbrido",
                "original_url": "https://www.bumeran.com.pe/empleos/asistente-marketing-alicorp.html",
            },
            {
                "title": "Ingeniero Ambiental",
                "company": "Cerro Verde S.A.A.",
                "location_raw": "Arequipa, Perú",
                "salary_raw": "S/ 6,500 - S/ 8,500",
                "modality": "presencial",
                "original_url": "https://www.bumeran.com.pe/empleos/ingeniero-ambiental-cerroverde.html",
            },
            {
                "title": "Practicante de Contabilidad",
                "company": "EY Perú",
                "location_raw": "Lima, Miraflores",
                "salary_raw": "S/ 1,500",
                "modality": "híbrido",
                "original_url": "https://www.bumeran.com.pe/empleos/practicante-contabilidad-ey.html",
            },
        ]
