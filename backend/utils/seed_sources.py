"""
Seed initial sources into the database.
"""


SOURCES = [
    {
        "name": "servir",
        "base_url": "https://app.servir.gob.pe/DifusionOfertasExterno/faces/consultas/ofertas_laborales.xhtml",
        "enabled": True,
        "last_status": "pending",
        "notes": "Portal oficial del sector público peruano. CAS, 728 y 276. Alta prioridad.",
    },
    {
        "name": "computrabajo",
        "base_url": "https://pe.computrabajo.com",
        "enabled": True,
        "last_status": "pending",
        "notes": "Mayor bolsa de empleo privada en Perú. Scraping DOM directo.",
    },
    {
        "name": "bumeran",
        "base_url": "https://www.bumeran.com.pe",
        "enabled": True,
        "last_status": "pending",
        "notes": "Requiere Playwright para renderizado JS. Fallback mock activo.",
    },
    {
        "name": "laborum",
        "base_url": "https://www.laborum.pe",
        "enabled": True,
        "last_status": "pending",
        "notes": "Requiere Playwright para renderizado JS. Fallback mock activo.",
    },
    {
        "name": "indeed",
        "base_url": "https://pe.indeed.com",
        "enabled": True,
        "last_status": "pending",
        "notes": "Meta-buscador global. Rotación de User-Agent. Fallback mock activo.",
    },
    {
        "name": "getonboard",
        "base_url": "https://www.getonbrd.com",
        "enabled": True,
        "last_status": "pending",
        "notes": "API REST pública. Especializado en tech jobs. Sin WAF agresivo.",
    },
    {
        "name": "jooble",
        "base_url": "https://pe.jooble.org",
        "enabled": True,
        "last_status": "pending",
        "notes": "Meta-buscador secundario. Tráfico móvil simulado. Fallback mock activo.",
    },
    {
        "name": "infojobs",
        "base_url": "https://www.infojobs.com.pe",
        "enabled": True,
        "last_status": "pending",
        "notes": "Bolsa de trabajo con foco en profesionales. Fallback mock activo.",
    },
    {
        "name": "opcionempleo",
        "base_url": "https://www.opcionempleo.com.pe",
        "enabled": True,
        "last_status": "pending",
        "notes": "Meta-buscador secundario. Foco en operativos y ventas. Fallback mock activo.",
    },
    {
        "name": "empleosperu",
        "base_url": "https://www.empleosperu.gob.pe",
        "enabled": False,
        "last_status": "experimental",
        "notes": "Portal del MTPE. Estructura dinámica, en evaluación.",
    },
]


def seed_sources():
    from backend.database import SessionLocal
    from backend.models import Source
    db = SessionLocal()
    try:
        for src_data in SOURCES:
            existing = db.query(Source).filter(Source.name == src_data["name"]).first()
            if not existing:
                src = Source(**src_data)
                db.add(src)
            else:
                # Update enabled status for existing sources
                if src_data.get("enabled") is not None:
                    existing.enabled = src_data["enabled"]
                if src_data.get("notes"):
                    existing.notes = src_data["notes"]
        db.commit()
    except Exception as e:
        print(f"Error seeding sources: {e}")
    finally:
        db.close()
