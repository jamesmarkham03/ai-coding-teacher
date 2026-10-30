import unittest

from tutor.bank import concepts_for, load_bank, questions_for
from tutor.scoring import START_SCORE, language_score, record_result, weakest_concept
from tutor.session import BANK_PATH
from tutor.show_scores import format_report


class ScoringTests(unittest.TestCase):
    def test_new_concept_starts_at_middle_then_moves_toward_100_on_right_answer(self):
        scores = record_result({}, "python", "lists", correct=True)
        self.assertEqual(scores["python"]["lists"]["score"], 65.0)  # 50 + 0.3 * 50
        self.assertEqual(scores["python"]["lists"]["attempts"], 1)

    def test_wrong_answer_moves_score_toward_zero(self):
        scores = record_result({}, "python", "lists", correct=False)
        self.assertEqual(scores["python"]["lists"]["score"], 35.0)  # 50 - 0.3 * 50

    def test_language_score_averages_tried_concepts_only(self):
        scores = {"python": {"lists": {"score": 80, "attempts": 2},
                             "strings": {"score": 60, "attempts": 1}}}
        self.assertEqual(language_score(scores, "python"), 70.0)
        self.assertIsNone(language_score(scores, "java"))

    def test_weakest_concept_treats_untried_as_middle(self):
        scores = {"python": {"lists": {"score": 80, "attempts": 2}}}
        concepts = ["lists", "dictionaries", "strings"]
        self.assertEqual(weakest_concept(scores, "python", concepts), "dictionaries")
        self.assertEqual(START_SCORE, 50)


class BankTests(unittest.TestCase):
    def setUp(self):
        self.bank = load_bank(BANK_PATH)

    def test_every_concept_has_a_quick_and_a_coding_question(self):
        for concept in concepts_for(self.bank, "python"):
            self.assertTrue(questions_for(self.bank, "python", concept, "quick"), concept)
            self.assertTrue(questions_for(self.bank, "python", concept, "coding"), concept)

    def test_format_report_handles_empty_scores(self):
        self.assertIn("No sessions yet", format_report({}))


if __name__ == "__main__":
    unittest.main()
