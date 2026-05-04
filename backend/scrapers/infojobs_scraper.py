"""
InfoJobs Peru scraper - HTML con requests y BeautifulSoup.
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
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "es-PE,es;q=0.9",
        })
        return f"{BASE}/jobsearch/search-results/list.xhtml?keyword={keyword}&page={page}"

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

            # Multiple selectors to increase chance of matching
            cards = soup.select(
                "li.ij-OfferList-item, div.ij-OfferCard, "
                "article[class*='offer'], div[class*='offer-item'], "
                "li[class*='offer']"
            )

            for card in cards:
                try:
                    title_el = card.select_one("h2 a, h3 a, a[class*='title'], a[class*='offerTitle']")
                    if not title_el:
                        continue
                    title = title_el.get_text(strip=True)
                    href = title_el.get("href", "")
                    url_job = href if href.startswith("http") else f"{BASE}{href}"

                    company_el = card.select_one("[class*='company'], [class*='ij-OfferCard-subtitle'], [class*='empresa']")
                    company = company_el.get_text(strip=True) if company_el else ""

                    location_el = card.select_one("[class*='location'], [class*='place'], [class*='lugar']")
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
                    logger.debug(f"[infojobs] card error: {e}")

            return jobs
        except Exception as e:
            logger.error(f"[infojobs] parse error: {e}")
            return []
