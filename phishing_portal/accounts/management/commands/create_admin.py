"""
Management command to create an admin superuser.
Usage: python manage.py create_admin
"""
from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Creates an admin superuser with username "admin" and password "admin"'

    def handle(self, *args, **options):
        username = 'admin'
        password = 'admin'
        email = 'admin@example.com'

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists. Updating...')
            )
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.role = User.Role.ADMIN
            user.email = email
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated user "{username}" with admin privileges!')
            )
        else:
            # Create new superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            # Set role after creation
            user.role = User.Role.ADMIN
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created superuser "{username}"!')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\nYou can now login with:')
        )
        self.stdout.write(f'  Username: {username}')
        self.stdout.write(f'  Password: {password}')
        self.stdout.write(f'  Admin URL: http://localhost:8000/admin/')

