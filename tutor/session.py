"""A study session: teach one concept, check it with quick questions, then a coding question.

Run with: python -m tutor learn [--language python] [--concept lists] [--prep NAME] [--review]
"""
from datetime import datetime

from tutor import paths
from tutor.bank import (concept_key, concepts_for, languages_in, load_bank, pick_question, split_key)
from tutor.history import load_history, log_event, seen_counts
from tutor.practice import ask_coding, ask_quick
from tutor.scoring import (concept_score, due_for_review, language_score, level_label, load_scores,
                           priority, record_result, save_scores)

HINT_WEIGHT = 0.5  # an answer that needed a hint moves the score half as far
MISS_WEIGHT = 1.0


def lesson_text(language, concept):
    lesson = paths.LESSONS_DIR / language / f"{concept}.md"
    if not lesson.exists():
        return f"(No lesson written yet for {language}:{concept}.)\n"
    return lesson.read_text(encoding="utf-8")


def choose_concept(bank, scores, language="python", concept=None, prep=None, review=False, now=None):
    """Return (language, concept, reason) for the next session."""
    now = now or datetime.now()
    if concept:
        languages = languages_in(bank) if language in (None, "any") else [language]
        for lang in languages:
            if concept in concepts_for(bank, lang):
                return lang, concept, "you asked for it"
        raise SystemExit(f"Unknown concept {concept!r} for {language}. Run: python -m tutor concepts")

    if review:
        due = due_for_review(scores, now)
        if due:
            top = due[0]
            return top["language"], top["concept"], f"due for review ({top['days_since']} days since last time)"
        print("Nothing is due for review yet. Picking your weakest concept instead.")

    if prep:
        candidates = {split_key(k): w for k, w in prep["concepts"].items()}
        candidates = {k: w for k, w in candidates.items() if k[1] in concepts_for(bank, k[0])}
        reason = f"most useful for {prep['name']}"
    else:
        languages = languages_in(bank) if language in (None, "any") else [language]
        candidates = {(lang, c): 1.0 for lang in languages for c in concepts_for(bank, lang)}
        reason = "your weakest area"
    if not candidates:
        raise SystemExit(f"No questions for language {language!r} yet.")
    (lang, name), _ = max(candidates.items(), key=lambda item: priority(scores, item[0][0], item[0][1], item[1], now))
    return lang, name, reason


def run_session(language, concept, bank, scores, *, quick_count=2, lesson=True, mode="learn",
                input_fn=input, out=print, solutions_dir=None):
    """Teach, check and test one concept, then save the results. Returns the list of outcomes."""
    out(f"\n=== {language.title()}: {concept} (now {concept_score(scores, language, concept)}, "
        f"{level_label(concept_score(scores, language, concept))}) ===\n")
    if lesson:
        out(lesson_text(language, concept))

    seen = seen_counts(load_history())
    outcomes = []  # (question, correct, weight)
    asked = []

    for _ in range(quick_count):
        question = pick_question(bank, seen, language, concept, "quick", concept_score(scores, language, concept),
                                 exclude=asked)
        if question is None:
            break
        asked.append(question["id"])
        outcomes.append((question, ask_quick(question, input_fn, out), 1.0))

    coding = pick_question(bank, seen, language, concept, "coding", concept_score(scores, language, concept))
    if coding is not None:
        result = ask_coding(coding, learn=True, solutions_dir=solutions_dir, input_fn=input_fn, out=out)
        weight = HINT_WEIGHT if result.hints and result.correct else MISS_WEIGHT
        outcomes.append((coding, result.correct, weight))

    for question, correct, weight in outcomes:
        record_result(scores, language, concept, correct, question["difficulty"], weight)
        log_event(mode=mode, language=language, concept=concept, qid=question["id"], correct=correct,
                  difficulty=question["difficulty"], kind=question["kind"])
    save_scores(scores)

    right = sum(1 for _, correct, _ in outcomes if correct)
    out(f"\nSession result: {right}/{len(outcomes)} correct.")
    out(f"{concept} score is now {concept_score(scores, language, concept)} "
        f"({level_label(concept_score(scores, language, concept))}).")
    out(f"{language.title()} average: {language_score(scores, language)}.")
    return outcomes


def run_learn(args, input_fn=input, out=print):
    """Entry point for `python -m tutor learn`."""
    bank = load_bank()
    scores = load_scores()
    prep = None
    if args.prep:
        from tutor.prep import load_prep
        prep = load_prep(args.prep)
    language, concept, reason = choose_concept(bank, scores, args.language, args.concept, prep, args.review)
    out(f"Today's concept: {language}:{concept} ({reason})")
    return run_session(language, concept, bank, scores, quick_count=args.quick, lesson=not args.review,
                       mode="review" if args.review else "learn", input_fn=input_fn, out=out)
