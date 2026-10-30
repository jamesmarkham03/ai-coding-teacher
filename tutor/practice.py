"""The interactive pieces shared by study sessions and mock interviews: a quick question and a coding question.

Every function takes `input_fn` and `out` so tests can feed answers in and read the output back.
"""
import re
import time
from dataclasses import dataclass
from pathlib import Path

from tutor import paths
from tutor.runners import check_solution, extension_for, starter_code

LETTERS = "abcdefgh"


@dataclass
class Outcome:
    correct: bool
    skipped: bool = False
    timed_out: bool = False
    hints: int = 0
    attempts: int = 0
    seconds: float = 0.0
    complexity_ok: bool = None  # only set in mock interviews


def normalize(text):
    """Make quick-answer checking forgiving about case, spaces and quote marks."""
    return re.sub(r"[\s'\"`]", "", str(text)).lower()


def accepted_answers(question):
    answer = question["answer"]
    return answer if isinstance(answer, list) else [answer]


def ask_quick(question, input_fn=input, out=print):
    """Ask one short question. Returns True if the answer is right."""
    out(f"\nQuick check ({question['difficulty']}): {question['prompt']}")
    for letter, option in zip(LETTERS, question.get("options", [])):
        out(f"   {letter}) {option}")
    reply = input_fn("Your answer: ")
    correct = normalize(reply) in {normalize(a) for a in accepted_answers(question)}
    if correct:
        out("Correct!")
    else:
        shown = accepted_answers(question)[0]
        if question.get("options"):
            shown = f"{shown}) {question['options'][LETTERS.index(shown)]}"
        out(f"Not quite. The answer is {shown}")
    if question.get("explanation"):
        out(f"Why: {question['explanation']}")
    return correct


def solution_path(question, folder=None):
    folder = Path(folder or paths.SOLUTIONS_DIR)
    return folder / f"{question['id']}{extension_for(question['language'])}"


def big_o_of(text):
    """Pull the first O(...) out of a string and normalize it, e.g. 'O(n log n)' -> 'o(nlogn)'."""
    match = re.search(r"o\s*\(([^)]*)\)", str(text), re.IGNORECASE)
    return "o(" + normalize(match.group(1)) + ")" if match else None


def ask_complexity(question, input_fn=input, out=print):
    """Interview-style follow-up: what is the time complexity? Returns True/False, or None if unknown."""
    expected = big_o_of(question.get("complexity", {}).get("time", ""))
    if expected is None:
        return None
    reply = input_fn("Interviewer: what is the time complexity of your solution? ")
    ok = big_o_of(reply) == expected
    target = question["complexity"]
    out("That matches." if ok else f"Expected time {target['time']} and space {target.get('space', '?')}.")
    return ok


def show_failures(result, out=print, limit=3):
    if result.error:
        out(f"  Problem: {result.error}")
    for failure in result.failures[:limit]:
        out(f"  Failed: {failure}")
    if len(result.failures) > limit:
        out(f"  ...and {len(result.failures) - limit} more")
    if result.output:
        out(f"  Your code printed: {result.output}")


def ask_coding(question, *, learn=True, deadline=None, solutions_dir=None, input_fn=input, out=print):
    """Give a coding question, let the student work in a file, and test the file on each Enter.

    learn=True allows hints and shows the reference solution after a skip.
    learn=False is interview style: no hints, no solution reveal, optional deadline (epoch seconds).
    """
    path = solution_path(question, solutions_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(starter_code(question), encoding="utf-8")

    out(f"\nCoding question ({question['difficulty']}, {question['language']}):")
    out(question["prompt"])
    out(f"\nWrite your answer in: {path}")
    started = time.time()
    outcome = Outcome(correct=False)

    options = "Enter = run tests" + (", 'hint', " if learn else ", ") + "'skip'"
    while True:
        remaining = ""
        if deadline:
            left = max(0, int(deadline - time.time()))
            remaining = f" [{left // 60}:{left % 60:02d} left]"
        reply = input_fn(f"Save the file. ({options}){remaining} ").strip().lower()
        outcome.seconds = time.time() - started

        if reply == "skip":
            outcome.skipped = True
            out("Skipped. This counts as a miss.")
            if learn:
                out("\nOne way to solve it:\n" + question["solution"])
            return outcome
        if reply == "hint":
            if not learn:
                out("No hints in interview mode. Talk through your thinking instead.")
            else:
                outcome.hints += 1
                out("Hint: " + question.get("hint", "Break the problem into the smallest case first."))
            continue
        if deadline and time.time() > deadline:
            outcome.timed_out = True
            out("Time is up for this interview.")
            return outcome

        outcome.attempts += 1
        result = check_solution(question, path.read_text(encoding="utf-8"))
        if result.passed:
            outcome.correct = True
            out("All tests passed!" if result.n_total > 1 else "Correct!")
            if learn and question.get("complexity"):
                c = question["complexity"]
                out(f"Typical complexity: time {c['time']}, space {c.get('space', '?')}.")
            return outcome
        out(f"{result.n_passed}/{result.n_total or '?'} tests passed.")
        show_failures(result, out)
        out("Fix the file and try again.")
