from apps.notifications.models import Notification


def create_notification(*, user, title, message, link=""):
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        link=link,
    )


def notify_users(*, user_ids, title, message, link=""):
    ids = list({uid for uid in user_ids if uid})
    if not ids:
        return []
    return Notification.objects.bulk_create(
        [
            Notification(user_id=uid, title=title, message=message, link=link)
            for uid in ids
        ]
    )


def notify_stage_change(*, candidate, from_stage, to_stage, actor):
    """Notify job owner / recruiters about a pipeline move."""
    from apps.accounts.models import Role, User

    recipient_ids = set(
        User.objects.filter(
            role__in=[Role.ADMIN, Role.RECRUITER],
            is_active=True,
        ).values_list("id", flat=True)
    )
    if candidate.job.created_by_id:
        recipient_ids.add(candidate.job.created_by_id)
    recipient_ids.discard(actor.id)

    title = "Stage change"
    message = (
        f"{candidate.first_name} {candidate.last_name} moved from "
        f"{from_stage.name} to {to_stage.name} ({candidate.job.title})."
    )
    link = f"/candidates/{candidate.id}"
    return notify_users(
        user_ids=recipient_ids,
        title=title,
        message=message,
        link=link,
    )


def notify_scorecard_due(*, interview, interviewer_ids):
    """Remind interviewers to submit a scorecard after the interview."""
    title = "Scorecard due"
    message = (
        f"Please submit a scorecard for your "
        f"{interview.get_type_display()} interview with {interview.candidate} "
        f"({interview.job.title}) after "
        f"{interview.scheduled_at.strftime('%Y-%m-%d %H:%M')}."
    )
    link = "/my-interviews"
    return notify_users(
        user_ids=interviewer_ids,
        title=title,
        message=message,
        link=link,
    )
