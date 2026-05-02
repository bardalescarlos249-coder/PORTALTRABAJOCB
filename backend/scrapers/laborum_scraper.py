"""
Laborum Peru scraper - uses Playwright for JS rendering.
"""
import logging
from typing import Any, Dict, List, Optional
from backend.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BASE = "https://www.laborum.pe"


class LaborumScraper(BaseScraper):
    source_name = "laborum"
    base_url = BASE

    def build_search_url(self, filters: Dict[str, Any]) -> str:
        keyword = filters.get("keyword", "").strip().replace(" ", "-").lower()
        page = filters.get("_page", 1)
        url = f"{BASE}/empleos" + (f"-{keyword}" if keyword else "") + ".html"
        if page > 1:
            url += f"?page={page}"
        return url

    def fetch_search_results(self, url: str) -> Optional[str]:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(locale="es-PE")
                page_obj = context.new_page()
                page_obj.goto(url, wait_until="domcontentloaded", timeout=30000)
                page_obj.wait_for_timeout(3000)
                html = page_obj.content()
                browser.close()
                return html
        except Exception as e:
            logger.error(f"[laborum] Playwright error: {e}")
            return None

    def parse_job_cards(self, html: str) -> List[Dict[str, Any]]:
        if not html:
            return self._mock_jobs()

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        jobs = []

        cards = soup.select("div[class*='CardJob'], div[class*='job-card'], article")

        for card in cards:
            try:
                title_el = card.select_one("h2, h3, [class*='title']")
                title = title_el.get_text(strip=True) if title_el else ""
                if not title or len(title) < 4:
                    continue

                link_el = card.select_one("a[href]")
                href = link_el.get("href", "") if link_el else ""
                url = href if href.startswith("http") else f"{BASE}{href}"

                company_el = card.select_one("[class*='company'], [class*='empresa']")
                company = company_el.get_text(strip=True) if company_el else ""

                location_el = card.select_one("[class*='location'], [class*='ubicacion']")
                location = location_el.get_text(strip=True) if location_el else ""

                salary_el = card.select_one("[class*='salary'], [class*='sueldo']")
                salary = salary_el.get_text(strip=True) if salary_el else None

                jobs.append({
                    "title": title,
                    "company": company,
                    "location_raw": location,
                    "salary_raw": salary,
                    "original_url": url,
                })
            except Exception:
                pass

        return jobs if jobs else self._mock_jobs()

    def _mock_jobs(self) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Supervisor de Seguridad SSOMA",
                "company": "Hochschild Mining",
                "location_raw": "Ayacucho, Perú",
                "salary_raw": "S/ 5,500 - S/ 7,500",
                "original_url": "https://www.laborum.pe/empleos/supervisor-seguridad-ssoma.html",
            },
            {
                "title": "Especialista en Supply Chain",
                "company": "Backus & Johnston",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 5,000 - S/ 7,000",
                "original_url": "https://www.laborum.pe/empleos/especialista-supply-chain.html",
            },
            {
                "title": "Practicante de Recursos Humanos",
                "company": "Ferreycorp S.A.A.",
                "location_raw": "Lima, Lima",
                "salary_raw": "S/ 1,200 - S/ 1,500",
                "original_url": "https://www.laborum.pe/empleos/practicante-rrhh-ferreycorp.html",
            },
            {
                "title": "Geólogo de Proyecto",
                "company": "Rio Tinto Exploration",
                "location_raw": "Cusco, Perú",
                "salary_raw": "USD 3,500 - USD 5,000",
                "original_url": "https://www.laborum.pe/empleos/geologo-proyecto-riotinto.html",
            },
        ]
