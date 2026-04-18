from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Create default users (admin + analyst)"

    def handle(self, *args, **kwargs):

        # Analyst user
        if not User.objects.filter(username='analyst').exists():
            analyst = User.objects.create_user(
                username='analyst',
                password='analyst123'
            )
            analyst.is_active = True
            analyst.save()
            self.stdout.write(self.style.SUCCESS("Analyst user created"))

        # Admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                password='admin123',
                # email='admin@example.com'
            )
            self.stdout.write(self.style.SUCCESS("Admin user created"))

        self.stdout.write(self.style.SUCCESS("Done"))