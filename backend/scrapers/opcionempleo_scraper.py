"""
OpcionEmpleo Peru scraper - HTML scraping limpio sin mocks.
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
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "es-PE,es;q=0.9",
        })
        if keyword:
            url = f"{BASE}/empleo-{keyword}.html"
        else:
            url = f"{BASE}/empleos.html"
        if page > 1:
            url += f"?p={page}"
        return url

    def fetch_search_results(self, url: str) -> Optional[str]:
        html = self.fetch(url)
        if html and len(html) > 2000:
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
                "li[class*='job'], article[class*='offer'], div[class*='jobCard']"
            )

            for card in cards:
                try:
                    title_el = card.select_one("h2 a, h3 a, a[class*='title'], [class*='offer-title'] a")
                    if not title_el:
                        continue
                    title = title_el.get_text(strip=True)
                    href = title_el.get("href", "")
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

            return jobs
        except Exception as e:
            logger.error(f"[opcionempleo] parse error: {e}")
            return []
