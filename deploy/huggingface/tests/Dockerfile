FROM python:3.12.8-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
COPY requirements-dev.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy source code
COPY . .

# Set environment variables (will be overridden by Space secrets)
ENV PYTHONPATH=./src \
    PYTHONUNBUFFERED=1 \
    HUGGING_FACE_HUB_TOKEN="" \
    GITHUB_TOKEN="" \
    HF_SPACE_URL=""

# Create a non-root user
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Create directories for test reports
RUN mkdir -p data/test_reports

# Create directories for test reports
RUN mkdir -p data/test_reports

# Default command runs the test suite with coverage
CMD ["pytest", "tests/", "-v", "--tb=short", "--cov=src", "--cov-report=term-missing", "--cov-report=json:data/test_reports/coverage.json", "--cov-report=html:data/test_reports/htmlcov", "--maxfail=999", "--durations=20", "-W", "ignore::DeprecationWarning"]
