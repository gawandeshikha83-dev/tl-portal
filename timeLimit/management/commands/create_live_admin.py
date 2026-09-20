from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create live admin user"

    def handle(self, *args, **options):
        User = get_user_model()

        username = "tladmin"
        email = "admin@tlportal.local"
        password = "Rgm@2026"

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f"User '{username}' already exists.")
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        self.stdout.write(
            self.style.SUCCESS(f"Admin '{username}' created successfully.")
        )