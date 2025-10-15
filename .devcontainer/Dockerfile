FROM python:3.11-slim

WORKDIR /app

# Systemabhängigkeiten
RUN apt-get update && apt-get install -y \
    make \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Nur Requirements kopieren und installieren
COPY requirements.txt .

# Virtuelle Umgebung erstellen und dependencies installieren
RUN python3 -m venv /app/.venv \
    && /app/.venv/bin/pip install --upgrade pip \
    && /app/.venv/bin/pip install --no-cache-dir -r requirements.txt

# Restliche Dateien kopieren
COPY . .

# PATH setzen
ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"

CMD ["make", "qa-check"]