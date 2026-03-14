import os
from django.core.management.base import BaseCommand
from apps.users.models import User

class Command(BaseCommand):
    help = 'Create a superuser if it does not exist'

    def handle(self, *args, **options):
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.uz')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser: {email}'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser with email {email} already exists'))
