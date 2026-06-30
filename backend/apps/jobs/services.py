from apps.jobs.constants import DEFAULT_PIPELINE_STAGES
from apps.jobs.models import PipelineStage


def seed_default_pipeline_stages():
    """Create global template stages (job=null). Idempotent."""
    if PipelineStage.objects.filter(job__isnull=True).exists():
        return 0

    PipelineStage.objects.bulk_create(
        [PipelineStage(job=None, **stage) for stage in DEFAULT_PIPELINE_STAGES]
    )
    return len(DEFAULT_PIPELINE_STAGES)


def copy_default_stages_to_job(job):
    """Copy default pipeline stages onto a job opening."""
    if job.pipeline_stages.exists():
        return

    PipelineStage.objects.bulk_create(
        [PipelineStage(job=job, **stage) for stage in DEFAULT_PIPELINE_STAGES]
    )
