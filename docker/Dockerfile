# syntax=docker/dockerfile:1

# ---- Stage 1: builder — install dependencies into a virtualenv ----
FROM python:3.11-slim AS builder

WORKDIR /build

COPY docker/requirements-dashboard.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements-dashboard.txt

# ---- Stage 2: runtime — copy only the venv + app code, no build tools ----
FROM python:3.11-slim AS runtime

RUN groupadd -r retailpulse && useradd -r -g retailpulse retailpulse

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY dashboard/ ./dashboard/
COPY data/processed/ ./data/processed/
COPY data/raw/products_master.csv ./data/raw/products_master.csv
COPY models/hybrid_metrics.json models/churn_metrics_tuned.json ./models/

RUN chown -R retailpulse:retailpulse /app
USER retailpulse

WORKDIR /app/dashboard
EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

ENTRYPOINT ["streamlit", "run", "Home.py", \
            "--server.port=8501", \
            "--server.address=0.0.0.0", \
            "--server.headless=true"]
