"""Mock interviews.

mock coding     timed, interview rules (no lesson, no hints, no solutions until the end), complexity follow-up
mock questions  conceptual and behavioral questions graded against a rubric of key points
"""
import json
import math
import random
import time
import uuid
from datetime import datetime

from tutor import paths
from tutor.bank import (DIFFICULTIES, concept_key, concepts_for, languages_in, load_bank, pick_question,
                        questions_for, split_key, target_difficulty)
from tutor.checklist import load_checklist
from tutor.history import load_history, log_event, seen_counts
from tutor.practice import ask_coding, ask_complexity
from tutor.scoring import concept_score, load_scores, priority, record_result, save_scores
from tutor.storage import read_json, write_json

MOCK_WEIGHT = 1.25  # interview conditions count a little more than relaxed practice
QA_WEIGHT = 0.7  # a conceptual answer says less about coding skill than a passing solution
QA_PASS = 0.6  # share of key points an answer must cover to count as good


def load_mocks():
    return read_json(paths.MOCKS_PATH, [])


def save_mock(entry):
    mocks = load_mocks()
    mocks.append(entry)
    write_json(paths.MOCKS_PATH, mocks)


# ---------------------------------------------------------------- mock coding

def pick_mock_problems(bank, scores, seen, language, count, prep=None, rng=random, now=None):
    """Choose `count` coding questions from different concepts, each a bit harder than the last."""
    now = now or datetime.now()
    if prep:
        weights = {split_key(k): w for k, w in prep["concepts"].items()}
    else:
        weights = {}
    languages = languages_in(bank) if language in (None, "any") else [language]
    candidates = []
    for lang in languages:
        for concept in concepts_for(bank, lang):
            if not questions_for(bank, lang, concept, "coding"):
                continue
            if prep and (lang, concept) not in weights:
                continue
            candidates.append((lang, concept, weights.get((lang, concept), 1.0)))
    chosen, used = [], set()
    for position in range(count):
        pool = [c for c in candidates if (c[0], c[1]) not in used] or candidates
        if not pool:
            break
        ranked = sorted(pool, key=lambda c: -priority(scores, c[0], c[1], c[2], now))
        lang, concept, _ = rng.choice(ranked[:3])  # a little randomness so mocks aren't identical
        used.add((lang, concept))
        bump = 12 * position  # later problems are pitched harder
        question = pick_question(bank, seen, lang, concept, "coding", concept_score(scores, lang, concept) + bump)
        chosen.append(question)
    return chosen


def run_mock_coding(language="python", count=2, minutes=30, prep=None, input_fn=input, out=print,
                    solutions_dir=None, rng=random):
    bank, scores, history = load_bank(), load_scores(), load_history()
    problems = pick_mock_problems(bank, scores, seen_counts(history), language, count, prep, rng)
    if not problems:
        raise SystemExit("No coding questions available for that selection.")

    out(f"\n=== MOCK CODING INTERVIEW: {len(problems)} problem(s), {minutes} minutes ===")
    out("Rules: no lesson, no hints, no solutions until the end. Think out loud as you work.")
    out("Press Enter at each prompt to run your tests as many times as you like.")
    deadline = time.time() + minutes * 60
    started = time.time()
    results = []

    for number, question in enumerate(problems, 1):
        out(f"\n--- Problem {number} of {len(problems)} ---")
        outcome = ask_coding(question, learn=False, deadline=deadline,
                             solutions_dir=solutions_dir or (paths.SOLUTIONS_DIR / "mock"),
                             input_fn=input_fn, out=out)
        if outcome.correct:
            outcome.complexity_ok = ask_complexity(question, input_fn, out)
        results.append((question, outcome))
        if outcome.timed_out:
            break

    return finish_mock_coding(results, started, minutes, out)


def finish_mock_coding(results, started, minutes, out=print):
    """Score the interview, reveal reference solutions for misses, and save the record."""
    scores = load_scores()
    entry_questions = []
    for question, outcome in results:
        record_result(scores, question["language"], question["concept"], outcome.correct,
                      question["difficulty"], MOCK_WEIGHT)
        log_event(mode="mock", language=question["language"], concept=question["concept"], qid=question["id"],
                  correct=outcome.correct, difficulty=question["difficulty"], kind="coding")
        entry_questions.append({"qid": question["id"], "concept": question["concept"], "correct": outcome.correct,
                                "seconds": round(outcome.seconds), "attempts": outcome.attempts,
                                "complexity_ok": outcome.complexity_ok})
    save_scores(scores)

    solved = sum(1 for _, o in results if o.correct)
    percent = round(100 * solved / len(results)) if results else 0
    used = round((time.time() - started) / 60, 1)
    save_mock({"id": uuid.uuid4().hex[:8], "ts": datetime.now().isoformat(timespec="seconds"), "type": "coding",
               "minutes_allowed": minutes, "minutes_used": used, "solved": solved, "total": len(results),
               "percent": percent, "questions": entry_questions})

    out(f"\n=== MOCK RESULT: {solved}/{len(results)} solved in {used} of {minutes} minutes ({percent}%) ===")
    for question, outcome in results:
        status = "solved" if outcome.correct else ("skipped" if outcome.skipped else "not solved")
        extra = f", {outcome.attempts} test runs, {round(outcome.seconds)}s"
        if outcome.complexity_ok is not None:
            extra += ", complexity " + ("right" if outcome.complexity_ok else "missed")
        out(f"  {question['id']:<34}{question['difficulty']:<8}{status}{extra}")
    for question, outcome in results:
        if not outcome.correct:
            out(f"\nOne way to solve {question['id']}:\n{question['solution']}")
    out("\nFeedback: " + coding_feedback(results))
    return results


def coding_feedback(results):
    if not results:
        return "No problems attempted."
    solved = [o for _, o in results if o.correct]
    notes = []
    if len(solved) == len(results):
        notes.append("You solved everything. Next time try the harder tier or a shorter time limit.")
    elif not solved:
        notes.append("Nothing passed this time. Go back to the lesson for the weakest concept, then retry.")
    else:
        notes.append("Partial. Review the reference solutions above and redo the missed concept with `learn`.")
    if any(o.attempts > 4 for o in solved):
        notes.append("You needed many test runs. Trace one example by hand before running code.")
    if any(o.complexity_ok is False for o in solved):
        notes.append("Practise stating time and space complexity out loud right after you finish.")
    return " ".join(notes)


# ---------------------------------------------------------------- mock questions

def load_interview_questions():
    return json.loads(paths.INTERVIEW_QA_PATH.read_text(encoding="utf-8"))


def grade_answer(question, answer):
    """Compare an answer with the rubric. Returns (covered points, missed points, share covered)."""
    text = answer.lower()
    covered, missed = [], []
    for point in question["key_points"]:
        hit = any(keyword in text for keyword in point["keywords"])
        (covered if hit else missed).append(point["point"])
    return covered, missed, len(covered) / len(question["key_points"])


def read_answer(input_fn=input, out=print):
    """Read a multi-line answer; a blank line ends it."""
    out("Type your answer (press Enter on an empty line when you are done):")
    lines = []
    while True:
        line = input_fn("> ")
        if not line.strip():
            break
        lines.append(line)
    return "\n".join(lines)


def tags_for_prep(prep):
    """Interview-question tags relevant to a prep plan (from its checklist items), plus behavioral."""
    items = {item["id"]: item for item in load_checklist()}
    tags = {items[i]["qa"] for i in prep.get("checklist", []) if i in items and "qa" in items[i]}
    return tags | {"behavioral"}


def pick_questions(questions, seen, count, category=None, prep=None, rng=random):
    """Pick the least-seen questions: a third behavioral, the rest technical (unless a category is given)."""
    if category:
        pool = [q for q in questions if q["tag"] == category or q["category"].lower() == category.lower()]
        return sorted(pool, key=lambda q: (seen.get(q["id"], 0), rng.random()))[:count]
    tags = tags_for_prep(prep) if prep else None
    technical = [q for q in questions if q["tag"] != "behavioral" and (tags is None or q["tag"] in tags)]
    behavioral = [q for q in questions if q["tag"] == "behavioral"]
    if prep and prep.get("concepts"):
        wanted = {split_key(k)[1] for k in prep["concepts"]}
        technical.extend(q for q in questions if q.get("concept") and split_key(q["concept"])[1] in wanted
                         and q not in technical)
    order = lambda q: (seen.get(q["id"], 0), rng.random())
    n_beh = min(len(behavioral), max(1, math.ceil(count / 3)))
    picked = sorted(behavioral, key=order)[:n_beh] + sorted(technical, key=order)[:count - n_beh]
    rng.shuffle(picked)
    return picked


def run_mock_questions(count=5, category=None, prep=None, input_fn=input, out=print, rng=random):
    questions = load_interview_questions()
    seen = seen_counts(load_history())
    picked = pick_questions(questions, seen, count, category, prep, rng)
    if not picked:
        raise SystemExit(f"No interview questions found for category {category!r}.")

    out(f"\n=== MOCK QUESTIONS INTERVIEW: {len(picked)} questions ===")
    out("Answer like you would out loud: short, structured, with an example.")
    scores = load_scores()
    answered = []
    for number, question in enumerate(picked, 1):
        out(f"\n--- Question {number} of {len(picked)} [{question['category']}] ---")
        out(question["prompt"])
        answer = read_answer(input_fn, out)
        covered, missed, share = grade_answer(question, answer)
        out(f"\nCovered {len(covered)} of {len(question['key_points'])} key points.")
        out("".join(f"  [x] {p}\n" for p in covered) + "".join(f"  [ ] {p}\n" for p in missed).rstrip("\n"))
        out("\nA good answer sounds like: " + question["sample_answer"])
        passed = share >= QA_PASS
        # Keyword matching can't read nuance, so you get the last word on whether it was a good answer.
        verdict = input_fn(f"Auto grade: {'good' if passed else 'needs work'}. Enter to accept, y = I nailed it, n = I missed it: ")
        if verdict.strip().lower() in ("y", "yes"):
            passed = True
        elif verdict.strip().lower() in ("n", "no"):
            passed = False
        answered.append((question, share, passed))
        log_event(mode="qa", tag=question["tag"], qid=question["id"], correct=passed, coverage=round(share, 2),
                  concept=question.get("concept", "").split(":")[-1] or None,
                  language=question.get("concept", "").split(":")[0] or None)
        if question.get("concept"):
            language, concept = split_key(question["concept"])
            record_result(scores, language, concept, passed, "medium", QA_WEIGHT)
    save_scores(scores)

    good = sum(1 for _, _, p in answered if p)
    save_mock({"id": uuid.uuid4().hex[:8], "ts": datetime.now().isoformat(timespec="seconds"), "type": "qa",
               "solved": good, "total": len(answered), "percent": round(100 * good / len(answered)),
               "questions": [{"qid": q["id"], "coverage": round(s, 2), "good": p} for q, s, p in answered]})
    out(f"\n=== RESULT: {good}/{len(answered)} answered well ===")
    weak = [q["category"] for q, _, p in answered if not p]
    if weak:
        out("Practise next: " + ", ".join(sorted(set(weak))) + "  (python -m tutor mock questions --category <tag>)")
    return answered
