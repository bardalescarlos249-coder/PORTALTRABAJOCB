# Job Intelligence Perú

Plataforma de extracción, normalización y análisis de ofertas laborales peruanas desde portales públicos. Diseñada con un entorno minimalista, profesional (estilo Apple) y un backend robusto con scrapers modulares.

## Tecnologías

- **Frontend:** React + Vite, TailwindCSS (Diseño UI premium "Apple-like"), Lucide-React.
- **Backend:** Python, FastAPI, SQLAlchemy, SQLite, Pydantic.
- **Scraping:** Requests, BeautifulSoup4, Playwright (para renderizado JS en Bumeran/Laborum).

## Instalación y Ejecución Local

### 1. Backend (FastAPI)

1. Abre una terminal y navega a la carpeta `job-intelligence-peru`.
2. Crea un entorno virtual e instala las dependencias:
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   # Instalar dependencias:
   pip install -r backend/requirements.txt
   ```
3. Instala los navegadores de Playwright para los scrapers avanzados:
   ```bash
   playwright install chromium
   ```
4. Inicia el servidor backend:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
   > El servidor estará disponible en http://localhost:8000 y la documentación interactiva en http://localhost:8000/docs.

### 2. Frontend (React + Vite)

1. Abre otra terminal y navega a la carpeta `frontend`:
   ```bash
   cd frontend
   ```
2. Instala los paquetes de Node.js:
   ```bash
   npm install
   ```
3. Inicia el entorno de desarrollo:
   ```bash
   npm run dev
   ```
   > Podrás ver la aplicación en http://localhost:5173.

## Despliegue en GitHub Pages

El frontend está configurado para manejar escenarios donde la API del backend no esté disponible. Si la API falla o no se encuentra (como en GitHub Pages), el frontend cargará automáticamente datos pre-scrapeados (Mock Data) desde `public/data/jobs.json`.

Para desplegarlo:
1. Sube tu proyecto a GitHub.
2. Configura las acciones de GitHub Pages para desplegar aplicaciones estáticas o simplemente sube los archivos compilados resultantes del comando `npm run build` en el frontend.

## Arquitectura de Scrapers

- `ServirScraper`: Usa peticiones GET/POST y BeautifulSoup (Sin bloqueo, muy confiable).
- `ComputrabajoScraper`: Usa Requests con headers robustos.
- `BumeranScraper` y `LaborumScraper`: Usan **Playwright** en modo headless para renderizar el contenido dinámico del frontend en Javascript.
- `IndeedScraper`: Desactivado por defecto. Su archivo `robots.txt` prohíbe el scraping.

## Estilo y Diseño
El frontend utiliza CSS personalizado combinado con TailwindCSS para ofrecer componentes `apple-card`, `apple-btn-primary`, sombras suaves, bordes redondeados consistentes y colores sobrios (`#fbfbfd`, `#1d1d1f`, azul de acento).
