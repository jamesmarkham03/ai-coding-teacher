"""Picking what to study next. The teaching itself is done by the /learn skill (Claude), which calls
`python -m tutor next`, `question` and `check` from tutor/cli.py and logs results with `record`.
"""
from datetime import datetime

from tutor import paths
from tutor.bank import concepts_for, languages_in, pick_question, split_key
from tutor.scoring import concept_score, due_for_review, priority

QUICK_PER_SESSION = 2  # two quick reps, then one coding question


def lesson_path(language, concept):
    return paths.LESSONS_DIR / language / f"{concept}.md"


def lesson_text(language, concept):
    lesson = lesson_path(language, concept)
    if not lesson.exists():
        return f"(No lesson written yet for {language}:{concept}.)\n"
    return lesson.read_text(encoding="utf-8")


def choose_concept(bank, scores, language="python", concept=None, prep=None, review=False, now=None, out=print):
    """Return (language, concept, reason) for the next session."""
    now = now or datetime.now()
    languages = languages_in(bank) if language in (None, "any") else [language]
    if concept:
        for lang in languages:
            if concept in concepts_for(bank, lang):
                return lang, concept, "you asked for it"
        raise SystemExit(f"Unknown concept {concept!r} for {language}. Run: python -m tutor concepts")

    if review:
        due = due_for_review(scores, now)
        if due:
            top = due[0]
            return top["language"], top["concept"], f"due for review ({top['days_since']} days since last time)"
        out("Nothing is due for review yet. Picking your weakest concept instead.")

    if prep:
        candidates = {split_key(k): w for k, w in prep["concepts"].items()}
        candidates = {k: w for k, w in candidates.items() if k[1] in concepts_for(bank, k[0])}
        reason = f"most useful for {prep['name']}"
    else:
        candidates = {(lang, c): 1.0 for lang in languages for c in concepts_for(bank, lang)}
        reason = "your weakest area"
    if not candidates:
        raise SystemExit(f"No questions for language {language!r} yet.")
    (lang, name), _ = max(candidates.items(), key=lambda item: priority(scores, item[0][0], item[0][1], item[1], now))
    return lang, name, reason


def suggest_questions(bank, scores, seen, language, concept, quick_count=QUICK_PER_SESSION):
    """The question ids for one session: some quick reps, then one coding question if the concept has one."""
    score = concept_score(scores, language, concept)
    chosen, quick_ids = [], []
    for _ in range(quick_count):
        question = pick_question(bank, seen, language, concept, "quick", score, exclude=quick_ids)
        if question is None:
            break
        quick_ids.append(question["id"])
        chosen.append(question)
    coding = pick_question(bank, seen, language, concept, "coding", score)
    if coding is not None:
        chosen.append(coding)
    return chosen
