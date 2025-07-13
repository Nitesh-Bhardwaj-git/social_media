from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates an initial superuser if none exists.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'adminuser'  # Change as needed
        email = 'admin@example.com'  # Change as needed
        password = 'adminpassword123'  # Change as needed

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} created.'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser {username} already exists.')) 