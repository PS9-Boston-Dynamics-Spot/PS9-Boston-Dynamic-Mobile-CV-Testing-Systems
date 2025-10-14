FROM python:3.11-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# Systemabhängigkeiten (z. B. make)
RUN apt-get update && apt-get install -y make && rm -rf /var/lib/apt/lists/*

# Requirements kopieren (nur für Caching)
COPY requirements.txt .

# Dependencies installieren
RUN pip install --no-cache-dir -r requirements.txt

# Projektdateien kopieren
COPY . .

# Standardbefehl (wird durch `docker compose run` überschrieben)
CMD ["make", "qa-check"]
