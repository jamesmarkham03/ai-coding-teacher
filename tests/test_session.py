import argparse
import unittest
from datetime import datetime, timedelta

from tests.helpers import Student, TempProgress
from tutor.bank import load_bank
from tutor.history import load_history
from tutor.scoring import load_scores, record_result, save_scores
from tutor.session import choose_concept, lesson_text, run_learn, run_session


class SessionLoopTests(TempProgress):
    def run_it(self, student, language="python", concept="lists", scores=None, quick_count=2):
        scores = scores if scores is not None else load_scores()
        outcomes = run_session(language, concept, load_bank(), scores, quick_count=quick_count,
                               input_fn=student, out=student.out, solutions_dir=self.root / "solutions")
        return outcomes, scores

    def test_full_loop_teaches_asks_tests_and_updates_the_bank_scores(self):
        student = Student(coding="solve")
        outcomes, _ = self.run_it(student)
        text = "\n".join(student.lines)
        self.assertIn("# Lists", text)  # the lesson was shown
        self.assertEqual([c for _, c, _ in outcomes], [True, True, True])  # 2 quick + 1 coding
        saved = load_scores()["python"]["lists"]
        self.assertEqual(saved["attempts"], 3)
        self.assertGreater(saved["score"], 70)  # three right answers from the 50 starting point
        self.assertEqual(len(load_history()), 3)
        self.assertIn("lists score is now", text)

    def test_wrong_answers_lower_the_score_and_a_skip_reveals_the_solution(self):
        student = Student(coding="skip", quick_correct=False)
        _, scores = self.run_it(student)
        self.assertLess(scores["python"]["lists"]["score"], 30)
        self.assertIn("One way to solve it:", "\n".join(student.lines))
        self.assertTrue(all(not e["correct"] for e in load_history()))

    def test_a_failed_test_run_shows_the_failure_then_a_fix_passes(self):
        student = Student(coding="hint")
        outcomes, _ = self.run_it(student, quick_count=0)
        text = "\n".join(student.lines)
        self.assertIn("Hint:", text)
        self.assertTrue(outcomes[0][1])
        self.assertEqual(outcomes[0][2], 0.5)  # a hint halves the weight

    def test_wrong_code_reports_failures_and_can_be_skipped(self):
        student = Student(coding="wrong")
        self.run_it(student, quick_count=0)
        text = "\n".join(student.lines)
        self.assertIn("tests passed", text)
        self.assertIn("Failed:", text)

    def test_other_languages_run_the_same_loop(self):
        for language, concept in (("sql", "joins"), ("javascript", "arrays")):
            outcomes, _ = self.run_it(Student(coding="solve"), language, concept)
            self.assertTrue(all(c for _, c, _ in outcomes), (language, concept))
            self.assertIn(concept, load_scores()[language])

    def test_concept_without_coding_questions_still_runs(self):
        outcomes, _ = self.run_it(Student(), "javascript", "async", quick_count=2)
        self.assertEqual(len(outcomes), 2)


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


class RunLearnTests(TempProgress):
    def test_run_learn_end_to_end_with_review_mode(self):
        save_scores(record_result({}, "python", "lists", True, now=datetime.now() - timedelta(days=30)))
        student = Student(coding="solve")
        args = argparse.Namespace(language="python", concept=None, prep=None, review=True, quick=1)
        run_learn(args, input_fn=student, out=student.out)
        text = "\n".join(student.lines)
        self.assertIn("python:lists", text)
        self.assertNotIn("# Lists", text)  # review mode skips the lesson
        self.assertEqual({e["mode"] for e in load_history()}, {"review"})


if __name__ == "__main__":
    unittest.main()
