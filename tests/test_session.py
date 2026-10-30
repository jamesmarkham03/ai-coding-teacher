import unittest
from datetime import datetime, timedelta

from tests.helpers import TempProgress
from tutor.bank import load_bank
from tutor.scoring import record_result
from tutor.session import choose_concept, lesson_text, suggest_questions


class ChooseConceptTests(TempProgress):
    def test_default_pick_is_the_weakest_python_concept(self):
        scores = {}
        for concept in ("lists", "dictionaries", "strings"):
            record_result(scores, "python", concept, True)
        record_result(scores, "python", "sets", False)  # weak
        language, concept, _ = choose_concept(load_bank(), scores, "python")
        self.assertEqual((language, concept), ("python", "sets"))

    def test_explicit_concept_can_be_found_without_a_language(self):
        language, concept, _ = choose_concept(load_bank(), {}, "any", "joins")
        self.assertEqual((language, concept), ("sql", "joins"))

    def test_review_picks_the_most_overdue_concept(self):
        scores = record_result({}, "python", "lists", True, now=datetime.now() - timedelta(days=20))
        record_result(scores, "python", "sets", True, now=datetime.now())
        language, concept, reason = choose_concept(load_bank(), scores, "python", review=True)
        self.assertEqual(concept, "lists")
        self.assertIn("review", reason)

    def test_review_with_nothing_due_falls_back_to_weakest(self):
        said = []
        _, _, reason = choose_concept(load_bank(), {}, "python", review=True, out=said.append)
        self.assertEqual(reason, "your weakest area")
        self.assertIn("Nothing is due", said[0])

    def test_prep_plan_weights_steer_the_pick(self):
        prep = {"name": "x", "concepts": {"python:graphs": 6, "python:lists": 1}}
        _, concept, reason = choose_concept(load_bank(), {}, "python", prep=prep)
        self.assertEqual(concept, "graphs")
        self.assertIn("x", reason)

    def test_unknown_concept_exits_with_a_helpful_message(self):
        with self.assertRaises(SystemExit):
            choose_concept(load_bank(), {}, "python", "nonsense")

    def test_lesson_text_falls_back_when_missing(self):
        self.assertIn("No lesson", lesson_text("python", "no-such-concept"))


class SuggestQuestionsTests(unittest.TestCase):
    def test_two_quick_then_one_coding(self):
        questions = suggest_questions(load_bank(), {}, {}, "python", "lists")
        self.assertEqual([q["kind"] for q in questions], ["quick", "quick", "coding"])
        self.assertEqual(len({q["id"] for q in questions}), 3)

    def test_concept_without_coding_questions_gets_only_quick_ones(self):
        questions = suggest_questions(load_bank(), {}, {}, "javascript", "async")
        self.assertEqual([q["kind"] for q in questions], ["quick", "quick"])

    def test_already_seen_questions_rotate_out(self):
        bank = load_bank()
        first = suggest_questions(bank, {}, {}, "python", "lists")
        seen = {q["id"]: 1 for q in first}
        second = suggest_questions(bank, {}, seen, "python", "lists")
        self.assertNotEqual(first[-1]["id"], second[-1]["id"])


if __name__ == "__main__":
    unittest.main()
