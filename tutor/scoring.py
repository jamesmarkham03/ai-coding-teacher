"""Keeps a 0-100 score for each concept and rolls them up into a score per language.

Scores are stored as {language: {concept: {"score", "attempts", "last_practiced"}}}.
"""
from datetime import datetime

from tutor import paths
from tutor.storage import read_json, write_json

START_SCORE = 50  # a concept you have never tried sits in the middle
# How far one answer moves the score (0.3 = 30% of the gap to 0 or 100).
# Higher reacts faster to recent answers; lower smooths out lucky guesses.
LEARNING_RATE = 0.3
MAX_RATE = 0.6

# Passing a hard question proves more than passing an easy one; missing an easy one says more
# than missing a hard one.
CORRECT_FACTOR = {"easy": 0.8, "medium": 1.0, "hard": 1.2}
WRONG_FACTOR = {"easy": 1.2, "medium": 1.0, "hard": 0.8}

LEVELS = ((85, "strong"), (65, "solid"), (40, "building"), (0, "weak"))


def load_scores(path=None):
    return read_json(path or paths.SCORES_PATH, {})


def save_scores(scores, path=None):
    write_json(path or paths.SCORES_PATH, scores)


def concept_entry(scores, language, concept):
    return scores.get(language, {}).get(concept)


def concept_score(scores, language, concept):
    """Current score for one concept, or START_SCORE if it has not been tried."""
    entry = concept_entry(scores, language, concept)
    return entry["score"] if entry else START_SCORE


def level_label(score):
    for floor, label in LEVELS:
        if score >= floor:
            return label


def record_result(scores, language, concept, correct, difficulty="medium", weight=1.0, now=None):
    """Move the concept's score toward 100 for a right answer, or 0 for a wrong one.

    `weight` scales the move: 0.5 for an answer that needed a hint, above 1 for mock interviews.
    """
    entry = scores.setdefault(language, {}).setdefault(
        concept, {"score": START_SCORE, "attempts": 0}
    )
    factor = (CORRECT_FACTOR if correct else WRONG_FACTOR)[difficulty]
    rate = min(MAX_RATE, LEARNING_RATE * factor * weight)
    target = 100 if correct else 0
    entry["score"] = round(entry["score"] + rate * (target - entry["score"]), 1)
    entry["attempts"] += 1
    entry["last_practiced"] = (now or datetime.now()).isoformat(timespec="seconds")
    return scores


def language_score(scores, language):
    """Average of the tried concepts for a language, or None if nothing is tried yet."""
    concepts = scores.get(language, {})
    if not concepts:
        return None
    return round(sum(c["score"] for c in concepts.values()) / len(concepts), 1)


def review_interval_days(score):
    """Stronger concepts can wait longer before a refresher (50 -> 6 days, 90 -> 10 days)."""
    return 1 + score / 10


def days_since(entry, now):
    if not entry or "last_practiced" not in entry:
        return None
    return (now - datetime.fromisoformat(entry["last_practiced"])).total_seconds() / 86400


def due_for_review(scores, now=None):
    """Practiced concepts that haven't been seen for longer than their interval, most overdue first."""
    now = now or datetime.now()
    due = []
    for language, concepts in scores.items():
        for concept, entry in concepts.items():
            elapsed = days_since(entry, now)
            if elapsed is None:
                continue
            overdue = elapsed - review_interval_days(entry["score"])
            if overdue > 0:
                due.append({"language": language, "concept": concept, "days_since": round(elapsed, 1),
                            "overdue_days": round(overdue, 1), "score": entry["score"]})
    return sorted(due, key=lambda d: -d["overdue_days"])


def priority(scores, language, concept, weight=1.0, now=None):
    """How much a concept needs attention: weak, important and overdue concepts rank highest."""
    value = (100 - concept_score(scores, language, concept)) * weight
    elapsed = days_since(concept_entry(scores, language, concept), now or datetime.now())
    if elapsed is not None and elapsed > review_interval_days(concept_score(scores, language, concept)):
        value += 10
    return value


def weakest_concept(scores, language, concepts, now=None):
    """Pick the concept that needs the most work, so the next session targets your gaps."""
    return max(concepts, key=lambda c: priority(scores, language, c, now=now))
