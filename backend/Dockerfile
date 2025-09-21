FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (rarely change - cached layer)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (cache layer - only rebuilds when requirements.txt changes)
COPY requirements.txt .

# Install Python dependencies (cached unless requirements.txt changes)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (runs when code changes, but deps are cached)
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]