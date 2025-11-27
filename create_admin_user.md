# Create Admin User Instructions

## Option 1: Using Docker (If you're running the app with Docker)

Run this command:
```bash
docker-compose exec web python phishing_portal/manage.py create_admin
```

## Option 2: Using Local Python Environment

1. First, make sure you have Django installed and are in a virtual environment:
   ```bash
   pip install -r requirements.txt
   ```

2. Then run:
   ```bash
   cd phishing_portal
   python manage.py create_admin
   ```

## After running the command:

You'll be able to login to the admin panel at:
- **URL**: http://localhost:8000/admin/
- **Username**: admin
- **Password**: admin

The command will:
- Create a superuser with username "admin" and password "admin"
- Set the role to ADMIN
- Enable staff and superuser privileges
- If the user already exists, it will update the password and privileges

