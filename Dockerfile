FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user and give it ownership of the app directory
RUN useradd -m appuser && chown -R appuser:appuser /app

# Switch to non-root user for runtime
USER appuser

# Set working directory to Django project root
WORKDIR /app/phishing_portal

# Run Django dev server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

