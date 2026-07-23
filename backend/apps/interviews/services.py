from apps.candidates.models import ActivityActionType
from apps.candidates.services import log_activity
from apps.notifications.models import Notification
from apps.notifications.services import notify_scorecard_due


def notify_interviewers(*, interview, interviewer_ids):
    """Create a notification for each assigned interviewer."""
    title = "Interview assigned"
    message = (
        f"You are assigned to a {interview.get_type_display()} interview "
        f"with {interview.candidate} for {interview.job.title} "
        f"on {interview.scheduled_at.strftime('%Y-%m-%d %H:%M')}."
    )
    link = "/my-interviews"
    notifications = [
        Notification(user_id=user_id, title=title, message=message, link=link)
        for user_id in interviewer_ids
    ]
    created = Notification.objects.bulk_create(notifications)
    notify_scorecard_due(interview=interview, interviewer_ids=interviewer_ids)
    return created


def log_interview_scheduled(*, interview, user):
    return log_activity(
        candidate=interview.candidate,
        user=user,
        action_type=ActivityActionType.INTERVIEW_SCHEDULED,
        description=(
            f"Interview scheduled: {interview.get_type_display()}, "
            f"{interview.scheduled_at.strftime('%Y-%m-%d %H:%M')}"
        ),
        metadata={
            "interview_id": interview.id,
            "type": interview.type,
            "scheduled_at": interview.scheduled_at.isoformat(),
            "job_id": interview.job_id,
        },
    )
