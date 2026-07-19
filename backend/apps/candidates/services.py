from apps.candidates.models import ActivityActionType, CandidateActivity, CandidateStatus


def log_activity(*, candidate, user, action_type, description, metadata=None):
    """Create a CandidateActivity audit log entry."""
    return CandidateActivity.objects.create(
        candidate=candidate,
        user=user,
        action_type=action_type,
        description=description,
        metadata=metadata or {},
    )


def log_candidate_created(*, candidate, user):
    return log_activity(
        candidate=candidate,
        user=user,
        action_type=ActivityActionType.CREATED,
        description=f"Candidate added to {candidate.job.title}",
        metadata={
            "job_id": candidate.job_id,
            "job_title": candidate.job.title,
            "stage_id": candidate.current_stage_id,
            "stage_name": candidate.current_stage.name,
        },
    )


def move_candidate_stage(*, candidate, stage, reason, user):
    """Move candidate to a new stage, update status, and log the change."""
    if stage.job_id != candidate.job_id:
        raise ValueError("Stage must belong to the candidate's job.")

    from_stage = candidate.current_stage
    if from_stage.id == stage.id:
        raise ValueError("Candidate is already in this stage.")

    candidate.current_stage = stage

    if stage.name == "Rejected":
        candidate.status = CandidateStatus.REJECTED
    elif stage.name == "Hired":
        candidate.status = CandidateStatus.HIRED
    else:
        candidate.status = CandidateStatus.ACTIVE

    candidate.save(update_fields=["current_stage", "status", "updated_at"])

    log_activity(
        candidate=candidate,
        user=user,
        action_type=ActivityActionType.STAGE_CHANGE,
        description=f"Moved from {from_stage.name} to {stage.name}",
        metadata={
            "from_stage_id": from_stage.id,
            "from_stage_name": from_stage.name,
            "to_stage_id": stage.id,
            "to_stage_name": stage.name,
            "reason": reason,
        },
    )

    return candidate
