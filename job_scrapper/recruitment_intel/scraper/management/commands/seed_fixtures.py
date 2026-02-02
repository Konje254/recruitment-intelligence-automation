from django.core.management.base import BaseCommand
from scraper.models import Platform

class Command(BaseCommand):
    help = "Seed platform rows used by the fixture scraper."

    def handle(self, *args, **options):
        for name in ["indeed", "glassdoor", "linkedin"]:
            Platform.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS("Seeded platforms: indeed, glassdoor, linkedin"))
