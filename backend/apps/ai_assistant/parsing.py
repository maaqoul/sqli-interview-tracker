import json
import re


def extract_json(text: str):
    """Parse JSON from model output, tolerating optional markdown fences."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


def validate_questions(raw) -> list[dict]:
    if not isinstance(raw, list):
        raise ValueError("Expected a JSON array of questions.")

    allowed_types = {"technical", "behavioral"}
    allowed_diff = {"easy", "medium", "hard"}
    questions = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        question = str(item.get("question", "")).strip()
        q_type = str(item.get("type", "technical")).lower().strip()
        difficulty = str(item.get("difficulty", "medium")).lower().strip()
        if not question:
            continue
        if q_type not in allowed_types:
            q_type = "technical"
        if difficulty not in allowed_diff:
            difficulty = "medium"
        questions.append(
            {
                "question": question,
                "type": q_type,
                "difficulty": difficulty,
            }
        )

    if len(questions) < 8:
        raise ValueError("AI returned fewer than 8 valid questions.")
    return questions[:12]
