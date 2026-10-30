"""Shared test helpers: a temporary progress folder and a scripted "student" who answers prompts."""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tutor import paths
from tutor.bank import load_bank


class TempProgress(unittest.TestCase):
    """Points every personal-progress path at a throwaway folder so tests never touch real scores."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        patcher = mock.patch.multiple(
            paths,
            PROGRESS=root,
            SCORES_PATH=root / "scores.json",
            HISTORY_PATH=root / "history.json",
            MOCKS_PATH=root / "mocks.json",
            CHECKLIST_STATE_PATH=root / "checklist_state.json",
            PREP_DIR=root / "prep",
            SOLUTIONS_DIR=root / "solutions",
            COMPANIES_DIR=root / "companies",
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self._tmp.cleanup)
        self.root = root


class Student:
    """Plays the person at the keyboard. Records everything printed so it can answer the right question.

    coding: "solve" writes the reference solution, "skip" skips, "hint" asks for a hint once then solves,
            "wrong" leaves the starter file in place and runs the tests once, then skips.
    """

    def __init__(self, coding="solve", quick_correct=True, complexity_correct=True):
        self.bank = {q["id"]: q for q in load_bank()}
        self.by_prompt = {q["prompt"]: q for q in self.bank.values() if q["kind"] == "quick"}
        self.lines = []
        self.coding = coding
        self.quick_correct = quick_correct
        self.complexity_correct = complexity_correct
        self._hinted = False
        self._ran_wrong = False

    def out(self, text=""):
        self.lines.extend(str(text).splitlines() or [""])

    def _last(self, prefix):
        return next(line for line in reversed(self.lines) if line.startswith(prefix))

    def __call__(self, prompt=""):
        if prompt.startswith("Your answer"):
            text = self._last("Quick check").split("): ", 1)[1]
            # Multi-line prompts print their first line after "Quick check"; match on that.
            question = next(q for p, q in self.by_prompt.items() if p.splitlines()[0] == text)
            answer = question["answer"]
            return (answer[0] if isinstance(answer, list) else answer) if self.quick_correct else "zzz-wrong"
        if prompt.startswith("Save the file"):
            path = Path(self._last("Write your answer in: ").split(": ", 1)[1])
            question = self.bank[path.stem]
            if self.coding == "skip":
                return "skip"
            if self.coding == "wrong":
                if self._ran_wrong:
                    return "skip"
                self._ran_wrong = True
                return ""
            if self.coding == "hint" and not self._hinted:
                self._hinted = True
                return "hint"
            path.write_text(question["solution"], encoding="utf-8")
            return ""
        if prompt.startswith("Interviewer: what is the time complexity"):
            return "O(n^7)" if not self.complexity_correct else "It is O(" + "n" + ")"
        raise AssertionError(f"Unexpected prompt: {prompt!r}")
