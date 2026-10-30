import unittest

from tutor import paths
from tutor.bank import (concepts_for, languages_in, load_bank, pick_question, questions_for, target_difficulty)
from tutor.runners import check_solution


class BankContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = load_bank()

    def test_three_languages_in_expected_order(self):
        self.assertEqual(languages_in(self.bank), ["python", "sql", "javascript"])

    def test_every_concept_has_a_lesson_and_questions(self):
        for language in languages_in(self.bank):
            for concept in concepts_for(self.bank, language):
                lesson = paths.LESSONS_DIR / language / f"{concept}.md"
                self.assertTrue(lesson.exists(), f"missing lesson {lesson}")
                self.assertGreaterEqual(len(questions_for(self.bank, language, concept, "quick")), 2, concept)

    def test_python_and_sql_concepts_have_coding_questions(self):
        for language in ("python", "sql"):
            for concept in concepts_for(self.bank, language):
                self.assertTrue(questions_for(self.bank, language, concept, "coding"), f"{language}:{concept}")

    def test_multiple_choice_answers_point_at_a_real_option(self):
        for q in self.bank:
            if q.get("options"):
                letters = "abcdefgh"[:len(q["options"])]
                self.assertIn(q["answer"], list(letters), q["id"])

    def test_every_reference_solution_passes_its_own_tests(self):
        """The most important content check: if a reference solution fails, the test data or solution is wrong."""
        failures = []
        for q in self.bank:
            if q["kind"] != "coding":
                continue
            result = check_solution(q, q["solution"])
            if not result.passed:
                failures.append((q["id"], result.error, result.failures[:1]))
        self.assertEqual(failures, [])

    def test_a_do_nothing_starter_does_not_pass(self):
        from tutor.runners import starter_code
        for q in self.bank:
            if q["kind"] == "coding":
                self.assertFalse(check_solution(q, starter_code(q)).passed, q["id"])


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.bank = load_bank()

    def test_low_scores_get_easy_questions_and_high_scores_get_hard(self):
        self.assertEqual(target_difficulty(50), "easy")
        self.assertEqual(target_difficulty(65), "medium")
        self.assertEqual(target_difficulty(90), "hard")

    def test_unseen_questions_come_before_seen_ones(self):
        coding = questions_for(self.bank, "python", "lists", "coding")
        seen = {q["id"]: 3 for q in coding[:-1]}
        picked = pick_question(self.bank, seen, "python", "lists", "coding", 50)
        self.assertEqual(picked["id"], coding[-1]["id"])

    def test_difficulty_breaks_ties_between_equally_seen_questions(self):
        picked = pick_question(self.bank, {}, "python", "lists", "coding", 90)
        self.assertEqual(picked["difficulty"], "medium")  # lists has no hard question; medium is nearest

    def test_exclude_skips_ids_and_missing_kind_gives_none(self):
        first = pick_question(self.bank, {}, "python", "lists", "quick", 50)
        second = pick_question(self.bank, {}, "python", "lists", "quick", 50, exclude=[first["id"]])
        self.assertNotEqual(first["id"], second["id"])
        self.assertIsNone(pick_question(self.bank, {}, "javascript", "async", "coding", 50))


if __name__ == "__main__":
    unittest.main()
