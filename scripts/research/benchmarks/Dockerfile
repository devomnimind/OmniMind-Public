FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install minimal Python dependencies for benchmarks
COPY requirements-benchmark.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-benchmark.txt

# Copy source code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY pyproject.toml ./

# Create data and logs directories
RUN mkdir -p data logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "-c", "import sys; print('PYTHONPATH:', sys.path); import src.optimization.benchmarking"]