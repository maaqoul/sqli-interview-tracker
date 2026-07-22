from abc import ABC, abstractmethod


class AIService(ABC):
    """Provider-agnostic AI interface (OpenAI / Ollama / mock)."""

    @abstractmethod
    def generate_questions(
        self,
        job_title: str,
        level: str,
        skills: list[str],
        interview_type: str,
        n: int = 10,
    ) -> list[dict]:
        """Return list of {question, type, difficulty}."""

    @abstractmethod
    def summarize_feedback(self, scorecards: list, notes: list) -> dict:
        """Return strengths, concerns, recommendation, suggested_next_step."""

    @abstractmethod
    def mock_interview_turn(
        self,
        role: str,
        level: str,
        history: list,
        user_answer: str,
    ) -> dict:
        """Return feedback + next_question (or summary when done)."""
