# Usamos una imagen base de Python (versión a tu elección)
FROM python:3.11-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el archivo de requerimientos al contenedor
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código al contenedor
COPY . .

# Exponemos el puerto donde correrá nuestra app
EXPOSE 8000

# Comando por defecto para correr FastAPI con uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]