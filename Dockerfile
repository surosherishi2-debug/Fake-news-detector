# TruthLens-Omni Production Containerization
# Multi-stage, reproducible Python 3.12 image for verification and API serving

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    SEED=42

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy locked dependencies
COPY requirements-lock.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements-lock.txt

# Copy application codebase and artifacts
COPY src/ /app/src/
COPY data/ /app/data/
COPY experiments/ /app/experiments/
COPY docs/ /app/docs/
COPY scripts/ /app/scripts/
COPY tests/ /app/tests/
COPY run.py /app/run.py
COPY pyproject.toml /app/pyproject.toml
COPY README.md /app/README.md

# Expose FastAPI service port
EXPOSE 8000

# Health check against real endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Default command: launch interactive application runner
CMD ["python", "run.py"]
