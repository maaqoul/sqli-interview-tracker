import json
import urllib.error
import urllib.request

from django.conf import settings

from apps.ai_assistant.base import AIService
from apps.ai_assistant.parsing import extract_json, validate_questions
from apps.ai_assistant.prompts import (
    FEEDBACK_SUMMARIZER_SYSTEM,
    MOCK_INTERVIEW_SYSTEM,
    QUESTION_GENERATOR_SYSTEM,
    QUESTION_GENERATOR_USER,
)


class OllamaProvider(AIService):
    def __init__(self, model: str = "llama3"):
        self.model = model
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")

    def _chat(self, system: str, user: str) -> object:
        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc

        content = body.get("message", {}).get("content", "{}")
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
        data = self._chat(wrapped_system, user)
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
        data = self._chat(FEEDBACK_SUMMARIZER_SYSTEM, user)
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
        data = self._chat(system, user)
        if not isinstance(data, dict):
            raise ValueError("Invalid mock interview response.")
        return data
