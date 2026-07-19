from apps.candidates.models import ActivityActionType
from apps.candidates.services import log_activity
from apps.interviews.models import InterviewStatus


def finalize_scorecard_submission(*, scorecard, user):
    """Mark interview completed and log activity on candidate timeline."""
    interview = scorecard.interview
    if interview.status == InterviewStatus.SCHEDULED:
        interview.status = InterviewStatus.COMPLETED
        interview.save(update_fields=["status"])

    log_activity(
        candidate=interview.candidate,
        user=user,
        action_type=ActivityActionType.SCORECARD_SUBMITTED,
        description=(
            f"Scorecard submitted by {user.first_name} {user.last_name} "
            f"(Rating: {scorecard.overall_rating}/5)"
        ),
        metadata={
            "scorecard_id": scorecard.id,
            "interview_id": interview.id,
            "overall_rating": scorecard.overall_rating,
            "recommendation": scorecard.recommendation,
        },
    )
