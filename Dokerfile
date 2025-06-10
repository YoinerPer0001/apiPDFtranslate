FROM python:3.10-slim

# Instala LibreOffice y otras dependencias
RUN apt-get update && \
    apt-get install -y libreoffice && \
    apt-get clean

# Crea el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . .

# Instala dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expone el puerto para FastAPI (Render asigna su propio puerto, pero esto es necesario)
EXPOSE 10000

# Comando para ejecutar la app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
