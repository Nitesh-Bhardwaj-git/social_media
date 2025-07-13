from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create an initial superuser'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'admin'  # Change this to your desired username
        email = 'admin@example.com'  # Change this to your desired email
        password = 'admin111'  # Change this to a strong password
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS('Superuser created.'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists.')) 