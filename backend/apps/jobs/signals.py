from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.jobs.models import JobOpening
from apps.jobs.services import copy_default_stages_to_job


@receiver(post_save, sender=JobOpening)
def create_pipeline_stages_on_job_create(sender, instance, created, **kwargs):
    if created:
        copy_default_stages_to_job(instance)
