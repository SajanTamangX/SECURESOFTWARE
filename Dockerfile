# Development Dockerfile for Django Phishing Portal
# This Dockerfile creates a lightweight development environment using Python 3.11 slim image

# Base image: Python 3.11 slim (minimal Debian-based image for smaller size)
FROM python:3.11-slim

# Set working directory inside the container
# All subsequent commands will run in this directory
WORKDIR /app

# Copy all project files from host to container
# This includes source code, requirements.txt, templates, etc.
COPY . /app

# Install Python dependencies from requirements.txt
# --no-cache-dir: Don't store pip cache to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user for security best practices
# Running as root in containers is a security risk
# -m: Create home directory for the user
# chown: Give ownership of /app directory to appuser
RUN useradd -m appuser && chown -R appuser:appuser /app

# Switch to non-root user for runtime
# All commands after this will run as appuser (not root)
USER appuser

# Set working directory to Django project root
# This is where manage.py is located
WORKDIR /app/phishing_portal

# Run Django development server
# 0.0.0.0:8000 allows the server to accept connections from outside the container
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

