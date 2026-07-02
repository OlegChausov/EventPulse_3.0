FROM python:3.12-slim-bookworm

# ── Системные зависимости + Chrome ───────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    wget \
    unzip \
    curl \
    libglib2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libx11-6 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
 && rm -rf /var/lib/apt/lists/*

# ── Chrome/ChromeDriver пути (Linux/Docker) ───────────────────────
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver

WORKDIR /app

# ── Python зависимости ────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir huggingface_hub

# ── Скачиваем модель с Hugging Face Hub ───────────────────────────
RUN python -c "\
from huggingface_hub import snapshot_download; \
snapshot_download( \
    repo_id='OlegChausov/eventpulse-bge-m3', \
    local_dir='/app/bge-m3-posters', \
    ignore_patterns=['*.msgpack', '*.h5', 'flax_model*', 'tf_model*', 'rust_model*'] \
)"

# ── Копируем код приложения ───────────────────────────────────────
COPY . .
RUN chmod +x entrypoint.sh entrypoint_worker.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "Event_Pulse_app.main:app", "--host", "0.0.0.0", "--port", "8000"]