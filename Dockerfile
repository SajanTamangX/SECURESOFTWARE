FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user and give it ownership of the app directory
RUN useradd -m appuser && chown -R appuser:appuser /app

# Switch to non-root user for runtime
USER appuser

WORKDIR /app/phishing_portal

# Run Django dev server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

