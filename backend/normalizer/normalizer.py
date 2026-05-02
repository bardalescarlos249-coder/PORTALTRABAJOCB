"""
Normalizer - detects modality, seniority, salary, skills, career area.
"""
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


# ─── Modality ────────────────────────────────────────────────────────────────
MODALITY_RULES = [
    (["remoto", "remote", "teletrabajo", "trabajo remoto", "100% remoto"], "remoto"),
    (["híbrido", "hibrido", "hybrid", "mixto", "semi-presencial"], "híbrido"),
    (["presencial", "on-site", "onsite", "in-situ"], "presencial"),
]

def detect_modality(text: str) -> str:
    t = text.lower()
    for keywords, label in MODALITY_RULES:
        if any(kw in t for kw in keywords):
            return label
    return "no especificado"


# ─── Seniority ───────────────────────────────────────────────────────────────
SENIORITY_RULES = [
    (["practicante", "intern", "trainee", "egresado reciente"], "practicante"),
    (["auxiliar", "asistente", "assistant", "ayudante"], "asistente"),
    (["junior", "jr.", " jr ", "entry level", "entry-level"], "junior"),
    (["semi senior", "semi-senior", "semisenior"], "semi senior"),
    (["senior", "sr.", " sr ", "experto", "especialista"], "senior"),
    (["supervisor", "coordinador", "coordinator"], "supervisor"),
    (["jefe", "head", "líder", "lider", "lead "], "jefe"),
    (["gerente", "manager", "director", "vp ", "vice president"], "gerente"),
]

def detect_seniority(text: str) -> str:
    t = text.lower()
    for keywords, label in SENIORITY_RULES:
        if any(kw in t for kw in keywords):
            return label
    return "no especificado"


# ─── Salary ───────────────────────────────────────────────────────────────────
SALARY_PATTERNS = [
    (r"S/[\s.]*([\d,]+(?:\.\d+)?)\s*[-–a]\s*S/[\s.]*([\d,]+(?:\.\d+)?)", "PEN", "range"),
    (r"USD?\s*([\d,]+(?:\.\d+)?)\s*[-–a]\s*USD?\s*([\d,]+(?:\.\d+)?)", "USD", "range"),
    (r"S/[\s.]*([\d,]+(?:\.\d+)?)", "PEN", "single"),
    (r"([\d,]+)\s*soles?", "PEN", "single"),
    (r"USD?\s*([\d,]+(?:\.\d+)?)", "USD", "single"),
]

def extract_salary(text: str):
    if not text:
        return None, None, "no especificado"
    t = text.replace(",", "")
    for pattern, currency, kind in SALARY_PATTERNS:
        m = re.search(pattern, t, re.IGNORECASE)
        if m:
            if kind == "range":
                return float(m.group(1)), float(m.group(2)), currency
            else:
                val = float(m.group(1))
                return val, val, currency
    if re.search(r"a convenir|por acuerdo|no especificado|confidencial", t, re.IGNORECASE):
        return None, None, "no especificado"
    return None, None, "no especificado"


# ─── Skills ──────────────────────────────────────────────────────────────────
SKILL_KEYWORDS = [
    "Excel", "Power BI", "PowerBI", "SQL", "Python", "ArcGIS", "Leapfrog",
    "Datamine", "AutoCAD", "SAP", "ERP", "inglés", "ingles", "inglés avanzado",
    "licencia de conducir", "AutoCAD Civil 3D", "Micromine", "Surpac",
    "Vulcan", "GIS", "R Studio", "Tableau", "Google Analytics", "Scrum",
    "BCRP", "SUNAT", "SIAF", "SIGA", "Office", "Word", "PowerPoint",
    "JavaScript", "TypeScript", "React", "Node.js", "Django", "Machine Learning",
    "AWS", "Azure", "Docker", "Git",
]

def extract_skills(text: str) -> List[str]:
    found = []
    t = text.lower() if text else ""
    for skill in SKILL_KEYWORDS:
        if skill.lower() in t:
            found.append(skill)
    return list(dict.fromkeys(found))


# ─── Career Area ──────────────────────────────────────────────────────────────
CAREER_RULES = [
    ("Geología", ["geólogo", "geóloga", "geologia", "geología", "ore control", "mapeo geológico", "exploraciones", "geoquímica"]),
    ("Minería", ["minas", "minería", "planeamiento mina", "operaciones mina", "perforación", "voladura", "shotcrete"]),
    ("Ambiental", ["ambiental", "medio ambiente", "eia", "monitoreo ambiental", "cierre de minas", "gestión ambiental"]),
    ("Data & Analytics", ["analista de datos", "data analyst", "sql", "power bi", "analytics", "bi analyst", "data scientist", "machine learning"]),
    ("Logística", ["logística", "logistica", "cadena de suministro", "supply chain", "almacén", "almacen", "compras", "inventario"]),
    ("Administración", ["administración", "administracion", "gestión administrativa", "asistente administrativo", "secretaria"]),
    ("Marketing", ["marketing", "community manager", "publicidad", "branding", "digital marketing", "seo"]),
    ("Contabilidad & Finanzas", ["contabilidad", "contaduría", "finanzas", "tesorería", "auditoría", "costos"]),
    ("Recursos Humanos", ["recursos humanos", "rrhh", "gestión humana", "reclutamiento", "selección de personal"]),
    ("Seguridad", ["seguridad", "ssoma", "ssomac", "prevención de riesgos", "higiene industrial", "safety"]),
    ("Civil & Construcción", ["civil", "construcción", "construccion", "obra", "topografía", "topografia"]),
    ("Sistemas & TI", ["sistemas", "tecnología", "ti ", "developer", "programador", "software", "it ", "devops"]),
    ("Ingeniería Industrial", ["industrial", "lean", "six sigma", "procesos", "producción", "manufactura"]),
    ("Derecho", ["abogado", "abogada", "legal", "derecho", "jurídico", "compliance"]),
    ("Salud", ["médico", "médica", "enfermero", "enfermera", "salud", "clínico", "farmacia"]),
]

def detect_career_area(title: str, description: str = "") -> Optional[str]:
    combined = f"{title} {description}".lower()
    for area, keywords in CAREER_RULES:
        if any(kw in combined for kw in keywords):
            return area
    return "Otros"


# ─── Sector ──────────────────────────────────────────────────────────────────
def detect_sector(company: str, description: str = "") -> str:
    combined = f"{company} {description}".lower()
    if any(kw in combined for kw in ["ministerio", "municipalidad", "gobierno", "estado", "serv", "mef", "sunat", "midis"]):
        return "Público"
    if any(kw in combined for kw in ["minera", "mine", "antamina", "barrick", "southern", "tintaya", "cerro verde"]):
        return "Minería"
    if any(kw in combined for kw in ["banco", "financier", "intercorp", "credicorp", "bcp", "bbva", "interbank"]):
        return "Financiero"
    if any(kw in combined for kw in ["tech", "software", "sistemas", "digital", "startup"]):
        return "Tecnología"
    return "Privado"


# ─── Location ─────────────────────────────────────────────────────────────────
DEPARTMENTS = [
    "Lima", "Arequipa", "Cajamarca", "Pasco", "Junín", "Cusco", "Moquegua",
    "Áncash", "Ancash", "La Libertad", "Ica", "Piura", "Lambayeque", "Puno",
    "Huancavelica", "Ayacucho", "Apurímac", "Loreto", "Ucayali", "San Martín",
    "Madre de Dios", "Amazonas", "Huánuco", "Tumbes",
]

def detect_department(location_raw: str) -> Optional[str]:
    if not location_raw:
        return None
    for dept in DEPARTMENTS:
        if dept.lower() in location_raw.lower():
            return dept
    return None


# ─── Master Normalize Function ─────────────────────────────────────────────────
def normalize_job(raw: Dict[str, Any], source: str) -> Dict[str, Any]:
    title = raw.get("title", "").strip()
    company = raw.get("company", "").strip()
    location_raw = raw.get("location_raw", "").strip()
    description = raw.get("description", "") or ""
    salary_text = raw.get("salary_raw", "") or ""
    combined_text = f"{title} {description} {raw.get('requirements', '')} {raw.get('job_type', '')}"

    salary_min, salary_max, salary_currency = extract_salary(salary_text)
    if salary_min is None and salary_max is None:
        salary_min, salary_max, salary_currency = extract_salary(combined_text)

    return {
        "id": str(uuid.uuid4()),
        "source": source,
        "source_job_id": raw.get("source_job_id"),
        "title": title,
        "company": company,
        "location_raw": location_raw,
        "country": "Perú",
        "department": detect_department(location_raw) or raw.get("department"),
        "province_or_city": raw.get("province_or_city") or detect_department(location_raw),
        "district": raw.get("district"),
        "modality": detect_modality(combined_text) if raw.get("modality") in (None, "no especificado", "") else raw.get("modality"),
        "job_type": raw.get("job_type", "no especificado") or "no especificado",
        "seniority": detect_seniority(combined_text),
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_currency": salary_currency,
        "salary_raw": salary_text or None,
        "publication_date_raw": raw.get("publication_date_raw"),
        "publication_date_estimated": raw.get("publication_date_estimated"),
        "application_deadline": raw.get("application_deadline"),
        "description": (description[:5000] if description else None),
        "requirements": raw.get("requirements", "")[:3000] if raw.get("requirements") else None,
        "functions": raw.get("functions", "")[:2000] if raw.get("functions") else None,
        "benefits": raw.get("benefits", "")[:1000] if raw.get("benefits") else None,
        "education_required": raw.get("education_required"),
        "experience_required": raw.get("experience_required"),
        "skills_detected": extract_skills(combined_text),
        "career_area_detected": detect_career_area(title, description),
        "sector_detected": detect_sector(company, description),
        "original_url": raw.get("original_url", ""),
        "status": "active",
        "confidence_score": raw.get("confidence_score", 1.0),
    }
