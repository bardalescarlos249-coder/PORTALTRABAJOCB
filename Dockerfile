# Usa la imagen oficial de Microsoft que ya viene con Playwright y Chromium instalado
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Define el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de dependencias
COPY backend/requirements.txt /app/

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código del backend a la carpeta /app/backend
COPY backend /app/backend

# Render provee automáticamente la variable de entorno $PORT (por defecto suele ser 10000)
ENV PORT=10000

# Exponer el puerto
EXPOSE $PORT

# Comando para arrancar el servidor FastAPI, escuchando en el puerto que asigne Render
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
