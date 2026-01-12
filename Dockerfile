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

ARG DINOV2_URL="https://dl.fbaipublicfiles.com/dinov2/dinov2_vits14/dinov2_vits14_pretrain.pth"
ENV DINOV2_WEIGHTS="/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/src/third_party/dinov2/checkpoints/dinov2_vits14.pth"
RUN mkdir -p "$(dirname "$DINOV2_WEIGHTS")" \
    && curl -L "$DINOV2_URL" -o "$DINOV2_WEIGHTS" \
    && sha256sum "$DINOV2_WEIGHTS"

ENV PATH="/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/.venv"
ENV PYTHONPATH="/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/src"

COPY scripts/entrypoint.sh /scripts/entrypoint.sh
RUN chmod +x /scripts/entrypoint.sh \
    && apt-get update && apt-get install -y dos2unix \
    && dos2unix /scripts/entrypoint.sh
ENTRYPOINT ["/scripts/entrypoint.sh"]
