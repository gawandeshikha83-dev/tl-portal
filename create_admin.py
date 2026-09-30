import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = "admin"
password = os.environ.get("ADMIN_PASSWORD")

if password:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
        },
    )

    if created:
        user.set_password(password)
        user.save()
        print("Admin user created successfully.")
    else:
        print("Admin user already exists.")
else:
    print("ADMIN_PASSWORD is not set.")