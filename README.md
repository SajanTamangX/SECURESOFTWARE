# Secure Software - Phishing Portal

A comprehensive Django-based phishing awareness and security training platform designed to help organizations educate their employees about cybersecurity threats through simulated phishing campaigns.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start with Docker](#quick-start-with-docker)
- [Detailed Docker Setup](#detailed-docker-setup)
- [Production Deployment](#production-deployment)
- [Manual Setup (Without Docker)](#manual-setup-without-docker)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Common Commands](#common-commands)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)

## 🎯 Overview

This application is a phishing simulation and security awareness training platform that allows organizations to:

- Create and manage phishing email campaigns
- Track recipient interactions and responses
- Provide security training and educational content
- Monitor and audit security events
- Generate reports and analytics

Built with Django 5.x and PostgreSQL, the platform provides a robust foundation for security awareness training programs.

## ✨ Features

- **Campaign Management**: Create, schedule, and manage phishing email campaigns
- **Email Templates**: Pre-built and customizable email templates for various phishing scenarios
  - IT Security Alert
  - Password Reset
  - Payroll/Bank Details
  - Delivery Failure
  - HR Policy Update
  - General Internal Email
- **Recipient Management**: Upload and manage campaign recipients via CSV import
- **Email Tracking**: Track email opens, link clicks, and phishing reports
- **Dashboard & Analytics**: Track campaign performance and user engagement metrics
- **Inbox Feature**: View and manage received phishing simulation emails
- **Landing Pages**: Educational landing pages after clicking phishing links
- **Audit Logging**: Comprehensive security event logging and monitoring
- **User Roles**: Support for different user roles (Admin, Instructor, Viewer) with role-based access control
- **Email Testing**: Integrated MailHog for email testing in development
- **Security Middleware**: Built-in protection against common web attacks (XSS, CSRF)
- **Training Content**: Educational blog posts and training videos
- **Sticky Notes**: Personal notes feature for VIEWER role users
- **Export Functionality**: Export campaign recipients and events to CSV
- **Security Scanning**: Integrated Semgrep (SAST) and OWASP ZAP (DAST) for security testing

## 🔧 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Git** (for cloning the repository)

### Verify Installation

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# Check Git version
git --version
```

## 🚀 Quick Start with Docker

Get the application running in under 5 minutes:

```bash
# 1. Clone the repository
git clone https://github.com/SajanTamangX/SECURESOFTWARE
cd SECURESOFTWARE

# 2. Create environment file
cat > .env.dev << EOF
DB_NAME=phishing_db
DB_USER=phishing_user
DB_PASSWORD=phishing_pass
DB_HOST=db
DB_PORT=5432
DJANGO_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
DJANGO_DEBUG=1
EMAIL_HOST=mailhog
EMAIL_PORT=1025
DEFAULT_FROM_EMAIL=no-reply@securesoftware.local
EOF

# 3. Start all services
docker-compose up --build

# 4. In a new terminal, run migrations
docker-compose exec web python phishing_portal/manage.py migrate

# 5. Create superuser (optional)
docker-compose exec web python phishing_portal/manage.py createsuperuser

# 6. Access the application
# Web App: http://localhost:8000
# MailHog: http://localhost:8025
# Admin: http://localhost:8000/admin
```

## 📖 Detailed Docker Setup

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd SECURESOFTWARE
```

### Step 2: Create Environment File

Create a `.env.dev` file in the root directory with the following content:

```bash
# Database Configuration
DB_NAME=phishing_db
DB_USER=phishing_user
DB_PASSWORD=phishing_pass
DB_HOST=db
DB_PORT=5432

# Django Configuration
DJANGO_SECRET_KEY=your-secret-key-here-change-this-in-production
DJANGO_DEBUG=1

# Email Configuration (MailHog for development)
EMAIL_HOST=mailhog
EMAIL_PORT=1025
DEFAULT_FROM_EMAIL=no-reply@securesoftware.local
```

**Important**: Generate a secure secret key for production:
```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(50))'
```

### Step 3: Build and Start Services

Start all services (database, web server, and MailHog):

```bash
# Build images and start containers
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

This command will:
- Build the Docker image for the web application
- Start PostgreSQL database container
- Start MailHog email testing server
- Start the Django web server

### Step 4: Run Database Migrations

After the containers are running, execute database migrations:

```bash
# Run migrations
docker-compose exec web python phishing_portal/manage.py migrate
```

### Step 5: Create Superuser (Optional)

Create an admin user to access the Django admin panel:

```bash
docker-compose exec web python phishing_portal/manage.py createsuperuser
```

Follow the prompts to create your admin account.

### Step 6: Access the Application

Once everything is running, you can access:

- **Web Application**: http://localhost:8000
- **MailHog (Email Testing UI)**: http://localhost:8025
- **Django Admin Panel**: http://localhost:8000/admin

### Step 7: Verify Installation

Check that all services are running:

```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs -f

# View logs for a specific service
docker-compose logs -f web
docker-compose logs -f db
```

## 🏭 Production Deployment

For production deployment, use the production Docker Compose configuration:

### Step 1: Create Production Environment File

Create a `.env.production` file:

```bash
# Database Configuration
DB_NAME=phishing_db_prod
DB_USER=phishing_user_prod
DB_PASSWORD=your-strong-production-password-here
DB_HOST=db
DB_PORT=5432

# Django Configuration
DJANGO_SECRET_KEY=your-production-secret-key-here
DJANGO_DEBUG=0
DJANGO_PRODUCTION=1

# Email Configuration (Use your SMTP server)
EMAIL_HOST=smtp.yourdomain.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=your-email@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Allowed Hosts (comma-separated)
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Step 2: Build and Start Production Services

```bash
# Build and start production services
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python phishing_portal/manage.py migrate

# Collect static files (if needed)
docker-compose -f docker-compose.prod.yml exec web python phishing_portal/manage.py collectstatic --noinput

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python phishing_portal/manage.py createsuperuser
```

### Production Features

The production setup includes:
- **Gunicorn** WSGI server with 3 workers
- **Health checks** for database connectivity
- **Automatic restarts** on failure
- **Static file volume** for efficient serving
- **Security hardening** (HTTPS, secure cookies, etc.)

## 💻 Manual Setup (Without Docker)

If you prefer not to use Docker, follow these steps:

### Step 1: Clone Repository

```bash
git clone <your-repository-url>
cd SECURESOFTWARE
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install PostgreSQL

**macOS:**
```bash
brew install postgresql@16
brew services start postgresql@16
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download and install from: https://www.postgresql.org/download/windows/

### Step 5: Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Inside PostgreSQL, run:
CREATE DATABASE phishing_db;
CREATE USER phishing_user WITH PASSWORD 'phishing_pass';
ALTER ROLE phishing_user SET client_encoding TO 'utf8';
ALTER ROLE phishing_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE phishing_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE phishing_db TO phishing_user;
\q
```

### Step 6: Set Environment Variables

**macOS/Linux:**
```bash
export DB_NAME=phishing_db
export DB_USER=phishing_user
export DB_PASSWORD=phishing_pass
export DB_HOST=localhost
export DB_PORT=5432
export DJANGO_SECRET_KEY=your-secret-key-here
export DJANGO_DEBUG=1
export EMAIL_HOST=localhost
export EMAIL_PORT=1025
export DEFAULT_FROM_EMAIL=no-reply@securesoftware.local
```

**Windows (PowerShell):**
```powershell
$env:DB_NAME="phishing_db"
$env:DB_USER="phishing_user"
$env:DB_PASSWORD="phishing_pass"
$env:DB_HOST="localhost"
$env:DB_PORT="5432"
$env:DJANGO_SECRET_KEY="your-secret-key-here"
$env:DJANGO_DEBUG="1"
$env:EMAIL_HOST="localhost"
$env:EMAIL_PORT="1025"
$env:DEFAULT_FROM_EMAIL="no-reply@securesoftware.local"
```

### Step 7: Run Migrations

```bash
cd phishing_portal
python manage.py migrate
```

### Step 8: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 9: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 10: Run Development Server

```bash
python manage.py runserver
```

Access the application at http://localhost:8000

## 📁 Project Structure

```
SECURESOFTWARE/
├── docker-compose.yml          # Development Docker Compose configuration
├── docker-compose.prod.yml     # Production Docker Compose configuration
├── Dockerfile                  # Development Docker image
├── Dockerfile.production       # Production Docker image
├── requirements.txt            # Python dependencies
├── Makefile                    # Makefile with security scanning commands
├── .env.dev                    # Development environment variables (create this)
├── .env.production             # Production environment variables (create this)
│
├── phishing_portal/            # Main Django application
│   ├── accounts/               # User authentication and management
│   │   ├── models.py          # User models with role-based access
│   │   ├── views.py           # Authentication views
│   │   ├── forms.py           # Login forms
│   │   ├── decorators.py     # Role-based access decorators
│   │   ├── urls.py            # Account URLs
│   │   └── management/        # Management commands
│   │       └── commands/
│   │           └── create_admin.py  # Create admin user command
│   │
│   ├── campaigns/             # Campaign management
│   │   ├── models.py          # Campaign, EmailTemplate, Recipient models
│   │   ├── views.py           # Campaign views
│   │   ├── views_admin.py     # Admin views (audit logs)
│   │   ├── views_dashboard.py # Dashboard views
│   │   ├── views_export.py   # Export views (CSV exports)
│   │   ├── forms.py           # Campaign and template forms
│   │   ├── services.py        # Email sending and CSV import services
│   │   ├── utils.py           # Utility functions (logging)
│   │   ├── blog_posts.py      # Educational blog posts content
│   │   └── urls.py            # Campaign URLs
│   │
│   ├── phishing_portal/       # Django project settings
│   │   ├── settings.py        # Application settings
│   │   ├── urls.py            # Root URL configuration
│   │   ├── wsgi.py            # WSGI configuration
│   │   └── middleware/        # Custom middleware
│   │       └── security.py    # Security middleware (XSS protection)
│   │
│   ├── templates/             # HTML templates
│   │   ├── base.html         # Base template
│   │   ├── campaigns/        # Campaign templates
│   │   ├── admin/            # Admin templates
│   │   ├── instructor/       # Instructor templates
│   │   ├── viewer/           # Viewer templates
│   │   └── registration/     # Auth templates
│   │
│   ├── manage.py             # Django management script
│   └── db.sqlite3            # SQLite database (development only)
│
├── security/                  # Security testing tools
│   ├── run_zap_baseline.sh   # OWASP ZAP baseline scan script
│   └── reports/              # Security scan reports
│
├── scripts/                   # Utility scripts
│   └── semgrep_scan.sh       # Semgrep scanning script
│
├── create_admin_user.md      # Instructions for creating admin users
├── SETUP.md                  # Detailed setup instructions
├── SECURITY_HARDENING_REPORT.md  # Security hardening documentation
└── README.md                  # This file
```

## 🔐 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_NAME` | PostgreSQL database name | `phishing_db` |
| `DB_USER` | PostgreSQL username | `phishing_user` |
| `DB_PASSWORD` | PostgreSQL password | `phishing_pass` |
| `DB_HOST` | Database host | `db` (Docker) or `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DJANGO_SECRET_KEY` | Django secret key | Generated secure key |
| `DJANGO_DEBUG` | Debug mode (0 or 1) | `1` (dev) or `0` (prod) |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `EMAIL_HOST` | SMTP server host | `mailhog` (dev) |
| `EMAIL_PORT` | SMTP server port | `1025` |
| `EMAIL_USE_TLS` | Use TLS for email | `False` |
| `EMAIL_HOST_USER` | SMTP username | - |
| `EMAIL_HOST_PASSWORD` | SMTP password | - |
| `DEFAULT_FROM_EMAIL` | Default sender email | `no-reply@securesoftware.local` |
| `DJANGO_PRODUCTION` | Production mode flag | `0` |

## 🛠️ Common Commands

### Docker Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f web
docker-compose logs -f db

# Execute command in container
docker-compose exec web python phishing_portal/manage.py <command>

# Rebuild containers
docker-compose up --build

# View running containers
docker-compose ps
```

### Django Management Commands

```bash
# Run migrations
docker-compose exec web python phishing_portal/manage.py migrate

# Create superuser
docker-compose exec web python phishing_portal/manage.py createsuperuser

# Collect static files
docker-compose exec web python phishing_portal/manage.py collectstatic --noinput

# Create new migration
docker-compose exec web python phishing_portal/manage.py makemigrations

# Open Django shell
docker-compose exec web python phishing_portal/manage.py shell

# Run tests
docker-compose exec web python phishing_portal/manage.py test
```

### Database Commands

```bash
# Access PostgreSQL shell
docker-compose exec db psql -U phishing_user -d phishing_db

# Backup database
docker-compose exec db pg_dump -U phishing_user phishing_db > backup.sql

# Restore database
docker-compose exec -T db psql -U phishing_user phishing_db < backup.sql
```

## 🔧 Troubleshooting

### Issue: Port 8000 Already in Use

**Solution:**
```bash
# Find process using port 8000
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use port 8001 instead
```

### Issue: Database Connection Error

**Solution:**
```bash
# Check if database container is running
docker-compose ps

# Check database logs
docker-compose logs db

# Verify environment variables
docker-compose exec web env | grep DB_

# Restart database
docker-compose restart db
```

### Issue: Migration Errors

**Solution:**
```bash
# Reset migrations (WARNING: Deletes all data)
docker-compose exec web python phishing_portal/manage.py flush
docker-compose exec web python phishing_portal/manage.py migrate

# Or check migration status
docker-compose exec web python phishing_portal/manage.py showmigrations
```

### Issue: Docker Build Fails

**Solution:**
```bash
# Clean Docker cache
docker system prune -a

# Remove volumes and rebuild
docker-compose down -v
docker-compose up --build

# Check Docker logs
docker-compose logs web
```

### Issue: Module Not Found Errors

**Solution:**
```bash
# Rebuild container
docker-compose up --build

# Verify requirements.txt is copied
docker-compose exec web pip list

# Reinstall dependencies
docker-compose exec web pip install -r requirements.txt
```

### Issue: Permission Denied Errors

**Solution:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Or rebuild container
docker-compose down
docker-compose up --build
```

### Issue: Static Files Not Loading

**Solution:**
```bash
# Collect static files
docker-compose exec web python phishing_portal/manage.py collectstatic --noinput

# Check static files directory
docker-compose exec web ls -la phishing_portal/staticfiles/
```

## 🔒 Security Considerations

### Development

- Use strong, unique `DJANGO_SECRET_KEY`
- Never commit `.env.dev` or `.env.production` to version control
- Keep `DJANGO_DEBUG=1` only in development
- Use MailHog for email testing (not production SMTP)

### Production

- Set `DJANGO_DEBUG=0`
- Set `DJANGO_PRODUCTION=1`
- Use strong database passwords
- Configure proper `ALLOWED_HOSTS`
- Use HTTPS (configure reverse proxy like Nginx)
- Set up proper SMTP server for emails
- Regularly update dependencies
- Enable database backups
- Monitor security logs
- Use environment variables for all secrets

### Security Features

- CSRF protection enabled
- XSS protection middleware
- Clickjacking protection
- Security headers configured
- Custom security middleware for attack prevention
- Audit logging for security events

## 👥 User Roles and Permissions

The application supports three user roles with different access levels:

### ADMIN Role
- Full access to all features
- Can create, edit, and delete campaigns
- Can create and manage email templates
- Can view all campaigns and recipients
- Can access audit logs
- Can manage all users

### INSTRUCTOR Role
- Can create and manage campaigns
- Can create and manage email templates
- Can upload recipients via CSV
- Can send campaign emails
- Can view campaign analytics
- Cannot access audit logs or manage users

### VIEWER Role
- Can view campaigns they created (if any)
- Can view emails sent to their email address (inbox)
- Can access educational blog posts
- Can access training videos
- Can create and manage sticky notes
- Cannot create campaigns or templates

### Creating Admin Users

To create an admin user, use the custom management command:

**With Docker:**
```bash
docker-compose exec web python phishing_portal/manage.py create_admin
```

**Without Docker:**
```bash
cd phishing_portal
python manage.py create_admin
```

This creates a superuser with:
- Username: `admin`
- Password: `admin`
- Role: `ADMIN`

**Note**: Change the default password after first login!

## 🧪 Testing and Security Scanning

### Running Tests

```bash
# With Docker
docker-compose exec web python phishing_portal/manage.py test

# Without Docker
cd phishing_portal
python manage.py test
```

### Security Scanning with Semgrep

The project includes Semgrep for Static Application Security Testing (SAST):

```bash
# Install Semgrep
make semgrep-install

# Run security scan
make semgrep-scan

# Run scan with JSON output
make semgrep-scan-json
```

### Dynamic Security Testing with OWASP ZAP

The project includes OWASP ZAP for Dynamic Application Security Testing (DAST):

```bash
# Run ZAP baseline scan (local development)
bash security/run_zap_baseline.sh http://localhost:8000

# Run ZAP scan (Docker Compose)
bash security/run_zap_baseline.sh http://web:8000
```

Reports are saved to `security/reports/` directory.

## 📝 Additional Notes

- **Database**: The application uses PostgreSQL. SQLite (`db.sqlite3`) is only for local development without Docker.
- **Email Testing**: MailHog is included in the development Docker setup for testing emails without sending real emails.
- **Static Files**: Static files are collected in production and served via Gunicorn or a reverse proxy.
- **Logging**: Security events are logged to `phishing_portal/security.log`.
- **User Roles**: The application supports multiple user roles with different permissions (see User Roles section above).
- **Makefile**: The project includes a Makefile with convenient commands for security scanning (see `make help`).
- **Security Directory**: Contains OWASP ZAP scripts and security testing reports.

## 👥 Development Team

This project was developed by:

- **Himanshu** - Project Manager
- **Anjali** - Project Manager and Researcher
- **Shistata** - Threat Analyst
- **Sajan** - Security Tester
- **Roshan** - Full Stack Developer and Researcher



