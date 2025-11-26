# Setup Instructions

Follow these step-by-step commands to get the project running on your PC.

## Prerequisites

Make sure you have the following installed:
- **Git** (to clone the repository)
- **Python 3.12** or higher
- **PostgreSQL** (or use Docker)
- **Docker & Docker Compose** (recommended, easier setup)

---

## Option 1: Using Docker (Recommended - Easiest)

### Step 1: Clone the Repository
```bash
git clone <your-repository-url>
cd SECURESOFTWARE
```

### Step 2: Create Environment File
Create a file named `.env.dev` in the root directory with the following content:

```bash
# Create the .env.dev file
cat > .env.dev << EOF
DB_NAME=phishing_db
DB_USER=phishing_user
DB_PASSWORD=phishing_pass
DB_HOST=db
DB_PORT=5432
DJANGO_SECRET_KEY=your-secret-key-here-change-this-in-production
DJANGO_DEBUG=1
EMAIL_HOST=mailhog
EMAIL_PORT=1025
DEFAULT_FROM_EMAIL=no-reply@securesoftware.local
EOF
```

### Step 3: Build and Run with Docker Compose
```bash
# Build and start all services (database, web server, mailhog)
docker-compose up --build

# Or run in background (detached mode)
docker-compose up -d --build
```

### Step 4: Run Database Migrations
Open a new terminal and run:
```bash
# Execute migrations inside the Docker container
docker-compose exec web python phishing_portal/manage.py migrate
```

### Step 5: Create a Superuser (Optional - for admin access)
```bash
docker-compose exec web python phishing_portal/manage.py createsuperuser
```

### Step 6: Access the Application
- **Web Application**: http://localhost:8000
- **MailHog (Email Testing)**: http://localhost:8025
- **Admin Panel**: http://localhost:8000/admin

### To Stop the Services
```bash
docker-compose down
```

### To View Logs
```bash
docker-compose logs -f
```

---

## Option 2: Manual Setup (Without Docker)

### Step 1: Clone the Repository
```bash
git clone <your-repository-url>
cd SECURESOFTWARE
```

### Step 2: Create Python Virtual Environment
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
# Navigate to project root
cd /path/to/SECURESOFTWARE

# Install Python packages
pip install -r requirements.txt
```

### Step 4: Install PostgreSQL
**On macOS:**
```bash
brew install postgresql@16
brew services start postgresql@16
```

**On Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**On Windows:**
Download and install from: https://www.postgresql.org/download/windows/

### Step 5: Create PostgreSQL Database
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
**On macOS/Linux:**
```bash
export DB_NAME=phishing_db
export DB_USER=phishing_user
export DB_PASSWORD=phishing_pass
export DB_HOST=localhost
export DB_PORT=5432
export DJANGO_SECRET_KEY=your-secret-key-here-change-this-in-production
export DJANGO_DEBUG=1
export EMAIL_HOST=localhost
export EMAIL_PORT=1025
export DEFAULT_FROM_EMAIL=no-reply@securesoftware.local
```

**On Windows (PowerShell):**
```powershell
$env:DB_NAME="phishing_db"
$env:DB_USER="phishing_user"
$env:DB_PASSWORD="phishing_pass"
$env:DB_HOST="localhost"
$env:DB_PORT="5432"
$env:DJANGO_SECRET_KEY="your-secret-key-here-change-this-in-production"
$env:DJANGO_DEBUG="1"
$env:EMAIL_HOST="localhost"
$env:EMAIL_PORT="1025"
$env:DEFAULT_FROM_EMAIL="no-reply@securesoftware.local"
```

**Or create a `.env` file and use a package like `python-dotenv`** (you'll need to add it to requirements.txt)

### Step 7: Run Database Migrations
```bash
cd phishing_portal
python manage.py migrate
```

### Step 8: Create a Superuser (Optional)
```bash
python manage.py createsuperuser
```

### Step 9: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 10: Run the Development Server
```bash
python manage.py runserver
```

### Step 11: Access the Application
- **Web Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

---

## Troubleshooting

### Issue: Database connection error
**Solution**: Make sure PostgreSQL is running and the database credentials are correct.

### Issue: Port 8000 already in use
**Solution**: 
```bash
# Find and kill the process using port 8000
# On macOS/Linux:
lsof -ti:8000 | xargs kill -9
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: Module not found errors
**Solution**: Make sure you're in the virtual environment and all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Migration errors
**Solution**: 
```bash
# Reset migrations (WARNING: This will delete all data)
python manage.py flush
python manage.py migrate
```

### Issue: Docker build fails
**Solution**: 
```bash
# Clean Docker cache and rebuild
docker-compose down -v
docker system prune -a
docker-compose up --build
```

---

## Quick Start Commands Summary (Docker)

```bash
# 1. Clone repository
git clone <your-repository-url>
cd SECURESOFTWARE

# 2. Create .env.dev file (copy content from Step 2 above)

# 3. Start everything
docker-compose up --build

# 4. In another terminal, run migrations
docker-compose exec web python phishing_portal/manage.py migrate

# 5. Create superuser (optional)
docker-compose exec web python phishing_portal/manage.py createsuperuser

# 6. Access http://localhost:8000
```

---

## Notes

- The project uses PostgreSQL as the database
- MailHog is included for email testing (only in Docker setup)
- Make sure to change the `DJANGO_SECRET_KEY` in production
- The `DEBUG` setting should be set to `0` in production

