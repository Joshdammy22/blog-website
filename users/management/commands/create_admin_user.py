from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create admin user'

    def handle(self, *args, **kwargs):
        username = 'admin'
        password = 'HAVANA1234'
        email = 'oladokedamilola7@gmail.com'

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, password=password, email=email)
            self.stdout.write(self.style.SUCCESS('Successfully created admin user!'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))
