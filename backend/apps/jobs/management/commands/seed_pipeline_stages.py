from django.core.management.base import BaseCommand

from apps.jobs.services import seed_default_pipeline_stages


class Command(BaseCommand):
    help = "Seed global default pipeline stages (job=null templates)."

    def handle(self, *args, **options):
        created = seed_default_pipeline_stages()
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created {created} default pipeline stages."))
        else:
            self.stdout.write("Default pipeline stages already exist — skipped.")
