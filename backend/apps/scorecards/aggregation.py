"""Pure aggregation helpers for scorecard summaries (INT-033)."""

from collections import Counter

YES_RECOMMENDATIONS = frozenset({"strong_yes", "yes"})
SKILL_KEYS = (
    "technical",
    "communication",
    "problem_solving",
    "culture_fit",
    "leadership",
)


def _round1(value: float) -> float:
    return round(value * 10) / 10


def aggregate_scorecards(scorecards) -> dict:
    """Compute averages and Yes consensus from a queryset or list of Scorecard."""
    items = list(scorecards)
    count = len(items)
    if count == 0:
        return {
            "count": 0,
            "average_overall": None,
            "average_skills": {},
            "yes_count": 0,
            "consensus_label": "No scorecards yet",
            "breakdown": {},
        }

    average_overall = _round1(sum(s.overall_rating for s in items) / count)

    average_skills = {}
    for key in SKILL_KEYS:
        values = [
            s.skill_ratings[key]
            for s in items
            if isinstance(s.skill_ratings, dict) and key in s.skill_ratings
        ]
        if values:
            average_skills[key] = _round1(sum(values) / len(values))

    yes_count = sum(1 for s in items if s.recommendation in YES_RECOMMENDATIONS)
    breakdown = dict(Counter(s.recommendation for s in items))

    return {
        "count": count,
        "average_overall": average_overall,
        "average_skills": average_skills,
        "yes_count": yes_count,
        "consensus_label": f"{yes_count}/{count} recommend Yes",
        "breakdown": breakdown,
    }
