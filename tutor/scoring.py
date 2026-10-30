"""Keeps a 0-100 score for each concept and rolls them up into a score per language.

Scores are stored as {language: {concept: {"score": float, "attempts": int}}}.
"""
import json
from pathlib import Path

START_SCORE = 50  # a concept you have never tried sits in the middle
# How far one answer moves the score (0.3 = 30% of the gap to 0 or 100).
# Higher reacts faster to recent answers; lower smooths out lucky guesses.
LEARNING_RATE = 0.3


def load_scores(path):
    """Read saved scores, or start empty if the file does not exist yet."""
    path = Path(path)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_scores(scores, path):
    Path(path).write_text(json.dumps(scores, indent=2), encoding="utf-8")


def concept_score(scores, language, concept):
    """Current score for one concept, or START_SCORE if it has not been tried."""
    entry = scores.get(language, {}).get(concept)
    return entry["score"] if entry else START_SCORE


def record_result(scores, language, concept, correct):
    """Move the concept's score toward 100 for a right answer, or 0 for a wrong one."""
    entry = scores.setdefault(language, {}).setdefault(
        concept, {"score": START_SCORE, "attempts": 0}
    )
    target = 100 if correct else 0
    entry["score"] = round(entry["score"] + LEARNING_RATE * (target - entry["score"]), 1)
    entry["attempts"] += 1
    return scores


def language_score(scores, language):
    """Average of the tried concepts for a language, or None if nothing is tried yet."""
    concepts = scores.get(language, {})
    if not concepts:
        return None
    return round(sum(c["score"] for c in concepts.values()) / len(concepts), 1)


def weakest_concept(scores, language, concepts):
    """Pick the concept with the lowest score, so the next session targets your gaps."""
    return min(concepts, key=lambda c: concept_score(scores, language, c))
