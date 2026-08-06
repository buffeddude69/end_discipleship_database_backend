import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Creates a staff/superuser account from environment variables, but only
    if one with that username doesn't already exist. Safe to run on every
    deploy (e.g. as part of Render's Build Command) -- it's a no-op after
    the first successful run, so it never resets the password or errors
    out on later deploys.

    Required env vars: DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD
    Optional: DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_LEADER_ROLE,
    DJANGO_SUPERUSER_DEMOGRAPHY, DJANGO_SUPERUSER_GENDER, DJANGO_SUPERUSER_AREA
    """

    help = "Idempotently creates a superuser from environment variables, if one doesn't already exist."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username or not password:
            self.stdout.write(self.style.WARNING(
                "DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_PASSWORD not set "
                "-- skipping superuser creation."
            ))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Superuser '{username}' already exists -- skipping.")
            return

        User.objects.create_superuser(
            username=username,
            email=os.environ.get("DJANGO_SUPERUSER_EMAIL", ""),
            password=password,
            first_name=os.environ.get("DJANGO_SUPERUSER_FIRST_NAME", "Admin"),
            last_name=os.environ.get("DJANGO_SUPERUSER_LAST_NAME", "Account"),
            leader_role=os.environ.get(
                "DJANGO_SUPERUSER_LEADER_ROLE", User.LeaderRole.CAMPUS_MISSIONARY
            ),
            demography=os.environ.get(
                "DJANGO_SUPERUSER_DEMOGRAPHY", User.Demography.SINGLE_YOUNG_PRO
            ),
            gender=os.environ.get("DJANGO_SUPERUSER_GENDER", User.Gender.MALE),
            area=os.environ.get("DJANGO_SUPERUSER_AREA", User.Area.BINAN),
        )
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created."))
