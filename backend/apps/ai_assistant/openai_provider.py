from django.conf import settings

from apps.ai_assistant.base import AIService
from apps.ai_assistant.parsing import extract_json, validate_questions
from apps.ai_assistant.prompts import (
    FEEDBACK_SUMMARIZER_SYSTEM,
    MOCK_INTERVIEW_SYSTEM,
    QUESTION_GENERATOR_SYSTEM,
    QUESTION_GENERATOR_USER,
)


class OpenAIProvider(AIService):
    def __init__(self, model: str = "gpt-4o-mini"):
        from openai import OpenAI  # lazy import — avoids hard fail when unused

        self.model = model
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def _chat_json(self, system: str, user: str) -> object:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.4,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        content = response.choices[0].message.content or "{}"
        return extract_json(content)

    def generate_questions(
        self,
        job_title: str,
        level: str,
        skills: list[str],
        interview_type: str,
        n: int = 10,
    ) -> list[dict]:
        n = max(8, min(12, n))
        user = QUESTION_GENERATOR_USER.format(
            n=n,
            level=level,
            job_title=job_title,
            skills=", ".join(skills) if skills else "general",
            interview_type=interview_type,
        )
        wrapped_system = (
            QUESTION_GENERATOR_SYSTEM
            + ' Wrap the array in an object: {"questions": [...]}.'
        )
        data = self._chat_json(wrapped_system, user)
        if isinstance(data, dict):
            raw = data.get("questions", data.get("items", []))
        else:
            raw = data
        return validate_questions(raw)

    def summarize_feedback(self, scorecards: list, notes: list) -> dict:
        user = (
            "Summarize these scorecards and notes into a hiring brief.\n"
            f"Scorecards: {scorecards}\nNotes: {notes}\n"
            'Return JSON: {"strengths":[],"concerns":[],"recommendation":"",'
            '"suggested_next_step":""}'
        )
        data = self._chat_json(FEEDBACK_SUMMARIZER_SYSTEM, user)
        if not isinstance(data, dict):
            raise ValueError("Invalid feedback summary response.")
        return data

    def mock_interview_turn(
        self,
        role: str,
        level: str,
        history: list,
        user_answer: str,
    ) -> dict:
        system = MOCK_INTERVIEW_SYSTEM.format(level=level, role=role)
        user = (
            f"Conversation history: {history}\n"
            f"Candidate answer: {user_answer or '(start of interview)'}\n"
            "Return the next JSON turn."
        )
        data = self._chat_json(system, user)
        if not isinstance(data, dict):
            raise ValueError("Invalid mock interview response.")
        return data
