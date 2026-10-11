FROM python:3.12-slim

LABEL maintainer="arbitrage-team@example.com"
LABEL description="KuCoin Triangular Arbitrage Scanner - Production Deployment"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY tests/ ./tests/
COPY pyproject.toml .
COPY README.md .

# Create data directory for SQLite and reports
RUN mkdir -p /app/data /app/data/reports

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Run the application
CMD ["python", "-m", "kucoin_triangular_bot.main"]