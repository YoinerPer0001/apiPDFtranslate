FROM python:3.11-slim

# Instala LibreOffice y otras herramientas necesarias
RUN apt-get update && apt-get install -y libreoffice curl && apt-get clean

# Crea un directorio de trabajo
WORKDIR /app

# Copia archivos de la app
COPY . /app

# Instala las dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expone el puerto (FastAPI se ejecuta en 8000 por defecto)
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

