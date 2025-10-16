FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    make \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python3 -m venv /app/.venv \
    && /app/.venv/bin/pip install --upgrade pip \
    && /app/.venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"
ENV PYTHONPATH="/app/src" 