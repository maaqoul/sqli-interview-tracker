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
        return {
            "strengths": ["Strong technical fundamentals", "Clear communication"],
            "concerns": ["Limited leadership examples"],
            "recommendation": "yes",
            "suggested_next_step": "Proceed to final interview with hiring manager.",
        }

    def mock_interview_turn(
        self,
        role: str,
        level: str,
        history: list,
        user_answer: str,
    ) -> dict:
        turns = len([m for m in history if m.get("role") == "assistant"])
        if turns >= 3:
            return {
                "feedback": "Thanks for completing the practice session.",
                "next_question": "",
                "done": True,
                "summary": f"Solid practice for a {level} {role} interview.",
            }
        next_q = (
            f"Question {turns + 1}: "
            f"How would you approach this as a {level} {role}?"
        )
        return {
            "feedback": "Good answer — clear and structured." if user_answer else "",
            "next_question": next_q,
            "done": False,
        }
