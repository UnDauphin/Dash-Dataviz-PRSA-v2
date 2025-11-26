# Dockerfile
FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto que usa Dash
EXPOSE 8050

# Variable de entorno para evitar buffering
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=postgresql://dolphin:wVY2iozo2mojMJHo80TuCn1Ph3gK8YSe@dpg-d4j2nfa4d50c73fg5dkg-a.oregon-postgres.render.com/dashdb_a8hk

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]