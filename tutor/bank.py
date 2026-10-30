"""Loads the question bank and checks each question has the fields the session needs."""
import json
from pathlib import Path

BASE_FIELDS = {"id", "language", "concept", "kind", "prompt"}
KIND_FIELDS = {
    "quick": {"answer"},
    "coding": {"function", "tests"},
}


def load_bank(path):
    """Read every question and raise a clear error if one is incomplete."""
    questions = json.loads(Path(path).read_text(encoding="utf-8"))
    for question in questions:
        qid = question.get("id", "<no id>")
        if question.get("kind") not in KIND_FIELDS:
            raise ValueError(f"Question {qid} has unknown kind {question.get('kind')!r}")
        missing = (BASE_FIELDS | KIND_FIELDS[question["kind"]]) - question.keys()
        if missing:
            raise ValueError(f"Question {qid} is missing {sorted(missing)}")
    return questions


def questions_for(bank, language, concept, kind):
    """Return the questions for one concept of one language, of one kind."""
    return [
        q for q in bank
        if q["language"] == language and q["concept"] == concept and q["kind"] == kind
    ]


def concepts_for(bank, language):
    """List the concepts that have at least one question, in bank order, without repeats."""
    seen = []
    for q in bank:
        if q["language"] == language and q["concept"] not in seen:
            seen.append(q["concept"])
    return seen
