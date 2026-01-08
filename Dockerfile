FROM python:3.11-slim

WORKDIR /workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/

RUN apt-get update && apt-get install -y \
    make \
    build-essential \
    git \
    curl \
    sqlite3 \
    libgl1 \
    libglib2.0-0t64 \
    dos2unix \
    && ldconfig \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python3 -m venv /workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/.venv \
    && /workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/.venv/bin/pip install --upgrade pip \
    && /workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/.venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure the Spot SDK is available inside the container for downstream tools.
RUN rm -rf src/common/sdk/spot-sdk \
    && git clone https://github.com/boston-dynamics/spot-sdk.git src/common/sdk/spot-sdk

ENV PATH="/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/.venv"
ENV PYTHONPATH="/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/src"

COPY scripts/entrypoint.sh /scripts/entrypoint.sh
RUN chmod +x /scripts/entrypoint.sh \
    && apt-get update && apt-get install -y dos2unix \
    && dos2unix /scripts/entrypoint.sh
ENTRYPOINT ["/scripts/entrypoint.sh"]
