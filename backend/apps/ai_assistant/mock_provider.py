from apps.ai_assistant.base import AIService
from apps.ai_assistant.parsing import validate_questions


class MockProvider(AIService):
    """Deterministic provider for local demo and unit tests (no external API)."""

    def generate_questions(
        self,
        job_title: str,
        level: str,
        skills: list[str],
        interview_type: str,
        n: int = 10,
    ) -> list[dict]:
        skills_label = ", ".join(skills) if skills else "general skills"
        bank = [
            {
                "question": (
                    f"As a {level} {job_title}, how would you design a scalable "
                    f"service that uses {skills_label}?"
                ),
                "type": "technical",
                "difficulty": "hard",
            },
            {
                "question": f"Walk me through debugging a production issue in a {job_title} role.",
                "type": "technical",
                "difficulty": "medium",
            },
            {
                "question": "Explain how you would review a pull request for quality and security.",
                "type": "technical",
                "difficulty": "medium",
            },
            {
                "question": f"How do you stay current with tools relevant to {job_title}?",
                "type": "behavioral",
                "difficulty": "easy",
            },
            {
                "question": (
                    "Tell me about a time you disagreed with a teammate "
                    "on a technical decision."
                ),
                "type": "behavioral",
                "difficulty": "medium",
            },
            {
                "question": f"Describe a challenging delivery you led as a {level} engineer.",
                "type": "behavioral",
                "difficulty": "hard",
            },
            {
                "question": "How would you improve performance of a slow API endpoint?",
                "type": "technical",
                "difficulty": "hard",
            },
            {
                "question": "What testing strategy would you use for a critical business flow?",
                "type": "technical",
                "difficulty": "medium",
            },
            {
                "question": "Give an example of mentoring or knowledge sharing on your team.",
                "type": "behavioral",
                "difficulty": "easy",
            },
            {
                "question": f"How would you onboard into a new {job_title} project at SQLI?",
                "type": "behavioral",
                "difficulty": "easy",
            },
            {
                "question": "Design an authentication flow for a multi-tenant web app.",
                "type": "technical",
                "difficulty": "hard",
            },
            {
                "question": "How do you prioritize technical debt vs new features?",
                "type": "behavioral",
                "difficulty": "medium",
            },
        ]
        focus = interview_type.lower() if interview_type else ""
        if focus == "behavioral":
            ordered = [q for q in bank if q["type"] == "behavioral"] + [
                q for q in bank if q["type"] != "behavioral"
            ]
        elif focus in {"technical", "phone", "video", "onsite"}:
            ordered = [q for q in bank if q["type"] == "technical"] + [
                q for q in bank if q["type"] != "technical"
            ]
        else:
            ordered = bank

        count = max(8, min(12, n))
        return validate_questions(ordered[:count])

    def summarize_feedback(self, scorecards: list, notes: list) -> dict:
        if not scorecards:
            return {
                "strengths": [],
                "concerns": ["No scorecards submitted yet"],
                "recommendation": "neutral",
                "suggested_next_step": (
                    "Collect at least one interviewer scorecard before deciding."
                ),
            }

        strengths: list[str] = []
        concerns: list[str] = []
        ratings = []
        yes_votes = {"strong_yes", "yes"}
        yes_count = 0

        for sc in scorecards:
            ratings.append(sc.get("overall_rating") or 0)
            if sc.get("recommendation") in yes_votes:
                yes_count += 1
            if sc.get("strengths"):
                strengths.append(str(sc["strengths"]).strip())
            if sc.get("weaknesses"):
                concerns.append(str(sc["weaknesses"]).strip())

        for note in notes or []:
            if note:
                concerns.append(f"Note: {note}")

        avg = sum(ratings) / len(ratings) if ratings else 0
        if yes_count >= max(1, len(scorecards) // 2 + 1) or avg >= 4:
            recommendation = "yes"
            next_step = "Proceed to final interview with hiring manager."
        elif avg < 2.5 or yes_count == 0:
            recommendation = "no"
            next_step = "Consider rejecting or scheduling a remediation interview."
        else:
            recommendation = "neutral"
            next_step = "Hold a calibration meeting with interviewers."

        return {
            "strengths": strengths[:5] or ["Consistent engagement across interviews"],
            "concerns": concerns[:5] or ["No major concerns flagged"],
            "recommendation": recommendation,
            "suggested_next_step": next_step,
        }

    def mock_interview_turn(
        self,
        role: str,
        level: str,
        history: list,
        user_answer: str,
    ) -> dict:
        questions = [
            f"Welcome! I'll interview you for a {level} {role} role at SQLI. "
            f"First: why are you interested in this {role} position?",
            f"Describe a challenging problem you solved as a {level} engineer.",
            f"How would you design a reliable API for a {role} project?",
            "Tell me about a time you received critical feedback and how you used it.",
        ]

        # Start of session
        if not history and not user_answer:
            return {
                "feedback": "",
                "next_question": questions[0],
                "done": False,
            }

        answered = len([m for m in history if m.get("role") == "user"])
        # After 3 user answers, wrap up
        if answered >= 3:
            return {
                "feedback": "Nice closing answer — clear and thoughtful.",
                "next_question": "",
                "done": True,
                "summary": (
                    f"You completed a {level} {role} practice interview. "
                    "Strengths: structured answers. Focus next on deeper trade-offs."
                ),
            }

        next_idx = min(answered + 1, len(questions) - 1)
        return {
            "feedback": "Good answer — clear and structured." if user_answer else "",
            "next_question": questions[next_idx],
            "done": False,
        }
