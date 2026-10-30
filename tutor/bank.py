"""Loads the question bank (one JSON file per language) and picks the next question.

A concept is identified by language + name, written "python:lists" when one string is needed.
"""
import json
import random
from pathlib import Path

from tutor import paths

DIFFICULTIES = ("easy", "medium", "hard")
BASE_FIELDS = {"id", "language", "concept", "kind", "prompt"}
CODING_FIELDS = {
    "python": {"function|class", "tests", "solution"},
    "javascript": {"function|class", "tests", "solution"},
    "sql": {"setup", "expected", "solution"},
}


def concept_key(language, concept):
    return f"{language}:{concept}"


def split_key(key):
    language, concept = key.split(":", 1)
    return language, concept


def _validate(question, seen_ids):
    qid = question.get("id", "<no id>")
    if qid in seen_ids:
        raise ValueError(f"Duplicate question id {qid}")
    seen_ids.add(qid)

    missing = BASE_FIELDS - question.keys()
    if missing:
        raise ValueError(f"Question {qid} is missing {sorted(missing)}")
    if question["kind"] not in ("quick", "coding"):
        raise ValueError(f"Question {qid} has unknown kind {question['kind']!r}")
    if question.get("difficulty", "easy") not in DIFFICULTIES:
        raise ValueError(f"Question {qid} has unknown difficulty {question['difficulty']!r}")

    if question["kind"] == "quick":
        if "answer" not in question:
            raise ValueError(f"Question {qid} is missing 'answer'")
        return
    if question["language"] not in CODING_FIELDS:
        raise ValueError(f"Question {qid}: coding questions for {question['language']!r} aren't supported")
    for needed in CODING_FIELDS[question["language"]]:
        options = needed.split("|")
        if not any(option in question for option in options):
            raise ValueError(f"Question {qid} is missing {' or '.join(options)!r}")


TEXT_FIELDS = ("prompt", "solution", "setup", "starter", "hint")


def _join_lines(question):
    """Long text is easier to write in the bank as a list of lines; turn it back into one string."""
    for name in TEXT_FIELDS:
        if isinstance(question.get(name), list):
            question[name] = "\n".join(question[name])
    return question


def load_bank(directory=None):
    """Read every *.json file in the bank folder and check each question is complete."""
    directory = Path(directory or paths.BANK_DIR)
    questions, seen_ids = [], set()
    for file in sorted(directory.glob("*.json")):
        for question in json.loads(file.read_text(encoding="utf-8")):
            _join_lines(question)
            question.setdefault("difficulty", "easy")
            _validate(question, seen_ids)
            questions.append(question)
    return questions


def questions_for(bank, language, concept, kind=None):
    return [
        q for q in bank
        if q["language"] == language and q["concept"] == concept and (kind is None or q["kind"] == kind)
    ]


def concepts_for(bank, language):
    """Concepts that have at least one question, in bank order, without repeats."""
    seen = []
    for q in bank:
        if q["language"] == language and q["concept"] not in seen:
            seen.append(q["concept"])
    return seen


LANGUAGE_ORDER = ("python", "sql", "javascript")  # the order they were added; Python is the main one


def languages_in(bank):
    present = {q["language"] for q in bank}
    known = [lang for lang in LANGUAGE_ORDER if lang in present]
    return known + sorted(present - set(LANGUAGE_ORDER))


def all_concept_keys(bank):
    return [concept_key(lang, c) for lang in languages_in(bank) for c in concepts_for(bank, lang)]


def target_difficulty(score):
    """Match the question to how well the concept is known, so practice stays challenging."""
    if score < 55:
        return "easy"
    if score < 78:
        return "medium"
    return "hard"


def pick_question(bank, seen, language, concept, kind, score, exclude=()):
    """Pick the least-seen question, preferring one near the right difficulty.

    `seen` is {question id: times asked}. Returns None if the concept has no question of that kind.
    """
    pool = [q for q in questions_for(bank, language, concept, kind) if q["id"] not in exclude]
    if not pool:
        return None
    target = DIFFICULTIES.index(target_difficulty(score))

    def rank(question):
        gap = abs(DIFFICULTIES.index(question["difficulty"]) - target)
        return (seen.get(question["id"], 0), gap, random.random())

    return min(pool, key=rank)
