"""
Servir scraper - portal oficial del sector público peruano.
Usa el endpoint de búsqueda HTML sin mock fallback.
"""
import logging
import re
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from backend.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

SERVIR_BASE = "https://app.servir.gob.pe/DifusionOfertasExterno/faces/consultas/ofertas_laborales.xhtml"
SERVIR_LIST = "https://app.servir.gob.pe/DifusionOfertasExterno/rest/ofertaLaboral/listarOfertaLaboralPublico"


class ServirScraper(BaseScraper):
    source_name = "servir"
    base_url = SERVIR_BASE

    def build_search_url(self, filters: Dict[str, Any]) -> str:
        self._keyword = filters.get("keyword", "").lower()
        self.session.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Referer": SERVIR_BASE,
            "Origin": "https://app.servir.gob.pe",
        })
        return SERVIR_LIST

    def fetch_search_results(self, url: str) -> Optional[str]:
        try:
            payload = {"pagina": 1, "cantReg": 20, "descCargo": self._keyword or ""}
            response = self.session.post(url, json=payload, timeout=20)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            logger.warning(f"[servir] API error: {e}")
        return None

    def parse_job_cards(self, html: str) -> List[Dict[str, Any]]:
        if not html:
            return []
        try:
            import json
            data = json.loads(html)
            # Could be list directly or nested
            items = data if isinstance(data, list) else data.get("data", data.get("list", []))
            jobs = []
            for item in items:
                title = item.get("descCargo") or item.get("cargo") or item.get("titulo", "")
                company = item.get("entidad") or item.get("nombreEntidad", "SERVIR")
                location = item.get("region") or item.get("lugar", "Perú")
                salary = item.get("remuneracion") or item.get("sueldo")
                if salary:
                    salary = f"S/ {salary}"
                deadline = item.get("fecCierre") or item.get("fechaCierre")
                job_id = item.get("idOferta") or item.get("id", "")
                url = f"{SERVIR_BASE}#oferta-{job_id}" if job_id else SERVIR_BASE
                if title and len(title) > 3:
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location_raw": location,
                        "salary_raw": salary,
                        "application_deadline": str(deadline) if deadline else None,
                        "original_url": url,
                        "job_type": "CAS",
                        "sector_detected": "Público",
                    })
            return jobs
        except Exception as e:
            logger.error(f"[servir] parse error: {e}")
            # Fallback: try HTML scraping of the main page
            return self._parse_html_fallback(html)

    def _parse_html_fallback(self, html: str) -> List[Dict[str, Any]]:
        try:
            soup = BeautifulSoup(html, "lxml")
            jobs = []
            tables = soup.find_all("table")
            for t in tables:
                rows = t.find_all("tr")
                if len(rows) > 2:
                    for row in rows[1:]:
                        cells = row.find_all("td")
                        values = [c.get_text(strip=True) for c in cells]
                        if len(values) >= 3 and values[0] and len(values[0]) > 3:
                            links = [a["href"] for a in row.find_all("a", href=True) if not a["href"].startswith("javascript")]
                            jobs.append({
                                "title": values[0],
                                "company": values[1] if len(values) > 1 else "SERVIR",
                                "location_raw": values[2] if len(values) > 2 else "Perú",
                                "original_url": links[0] if links else SERVIR_BASE,
                                "job_type": "CAS",
                                "sector_detected": "Público",
                            })
            return jobs
        except Exception:
            return []
