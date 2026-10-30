import io
import random
import unittest
from contextlib import redirect_stdout

from tests.helpers import Student, TempProgress
from tutor import cli
from tutor.history import load_history
from tutor.mock import (coding_feedback, grade_answer, load_interview_questions, load_mocks, pick_mock_problems,
                        pick_questions, run_mock_coding, run_mock_questions)
from tutor.bank import load_bank
from tutor.practice import Outcome
from tutor.scoring import load_scores

QUESTIONS = {q["id"]: q for q in load_interview_questions()}


class GradingTests(unittest.TestCase):
    def test_answer_is_graded_by_key_points_covered(self):
        question = QUESTIONS["qa-py-list-tuple"]
        covered, missed, share = grade_answer(question, "Lists are mutable but a tuple is immutable.")
        self.assertEqual(len(covered), 1)
        self.assertEqual(len(missed), 2)
        self.assertAlmostEqual(share, 1 / 3)

    def test_full_answer_covers_everything_and_empty_covers_nothing(self):
        question = QUESTIONS["qa-db-acid"]
        _, missed, share = grade_answer(question, QUESTIONS["qa-db-acid"]["sample_answer"])
        self.assertEqual((missed, share), ([], 1.0))
        self.assertEqual(grade_answer(question, "")[2], 0)

    def test_every_sample_answer_passes_its_own_rubric(self):
        """If a sample answer can't pass its rubric, the keywords are wrong and good answers would be marked down."""
        for question in QUESTIONS.values():
            if question["tag"] == "behavioral":
                continue  # coaching guidance rather than a model answer
            self.assertGreaterEqual(grade_answer(question, question["sample_answer"])[2], 0.75, question["id"])

    def test_questions_are_well_formed(self):
        for q in QUESTIONS.values():
            self.assertTrue(q["key_points"] and q["sample_answer"] and q["tag"], q["id"])
            for point in q["key_points"]:
                self.assertTrue(point["keywords"], q["id"])


class PickingTests(TempProgress):
    def test_mock_problems_are_from_different_concepts_and_get_harder(self):
        problems = pick_mock_problems(load_bank(), {}, {}, "python", 3, rng=random.Random(1))
        self.assertEqual(len({p["concept"] for p in problems}), 3)
        self.assertTrue(all(p["kind"] == "coding" for p in problems))

    def test_prep_plan_restricts_mock_problems(self):
        prep = {"concepts": {"sql:joins": 3, "sql:aggregation": 2}}
        problems = pick_mock_problems(load_bank(), {}, {}, "any", 2, prep, rng=random.Random(2))
        self.assertTrue(all(p["language"] == "sql" for p in problems))

    def test_question_mix_has_behavioral_and_technical_and_respects_category(self):
        picked = pick_questions(list(QUESTIONS.values()), {}, 6, rng=random.Random(3))
        tags = [q["tag"] for q in picked]
        self.assertIn("behavioral", tags)
        self.assertTrue(any(t != "behavioral" for t in tags))
        only_git = pick_questions(list(QUESTIONS.values()), {}, 5, category="git")
        self.assertEqual({q["tag"] for q in only_git}, {"git"})

    def test_least_seen_questions_come_first(self):
        seen = {qid: 5 for qid in QUESTIONS if qid != "qa-git-undo"}
        self.assertEqual(pick_questions(list(QUESTIONS.values()), seen, 1, category="git")[0]["id"], "qa-git-undo")


class MockCodingTests(TempProgress):
    def test_mock_coding_scores_saves_and_reveals_solutions_for_misses(self):
        student = Student(coding="solve")
        run_mock_coding("python", 2, 30, input_fn=student, out=student.out, solutions_dir=self.root / "m", rng=random.Random(4))
        text = "\n".join(student.lines)
        self.assertIn("MOCK CODING INTERVIEW", text)
        self.assertIn("MOCK RESULT: 2/2", text)
        self.assertIn("complexity right", text)
        mock_entry = load_mocks()[0]
        self.assertEqual((mock_entry["type"], mock_entry["solved"], mock_entry["percent"]), ("coding", 2, 100))
        self.assertEqual({e["mode"] for e in load_history()}, {"mock"})
        self.assertEqual(len(load_scores()["python"]), 2)

    def test_interview_rules_hint_is_refused_and_misses_reveal_solutions_at_the_end(self):
        student = Student(coding="skip")
        run_mock_coding("python", 1, 30, input_fn=student, out=student.out, solutions_dir=self.root / "m", rng=random.Random(5))
        text = "\n".join(student.lines)
        self.assertNotIn("Hint:", text)
        self.assertIn("One way to solve", text)
        self.assertEqual(load_mocks()[0]["solved"], 0)

    def test_wrong_complexity_answer_is_flagged(self):
        student = Student(coding="solve", complexity_correct=False)
        run_mock_coding("python", 1, 30, input_fn=student, out=student.out, solutions_dir=self.root / "m", rng=random.Random(6))
        self.assertIn("Expected time", "\n".join(student.lines))

    def test_feedback_text_reacts_to_results(self):
        self.assertIn("solved everything", coding_feedback([(None, Outcome(True, attempts=1))]))
        self.assertIn("Nothing passed", coding_feedback([(None, Outcome(False))]))
        self.assertIn("many test runs", coding_feedback([(None, Outcome(True, attempts=6, complexity_ok=False))]))


class MockQuestionsTests(TempProgress):
    def test_mock_questions_grade_log_and_update_concept_scores(self):
        answers = iter(["Lists are mutable, tuples are immutable and hashable, use a tuple for a fixed record.", "",
                        ""])  # answer, blank line ends it, Enter accepts auto grade
        collected = []
        run_mock_questions(1, category="python", input_fn=lambda prompt="": next(answers), out=collected.append,
                           rng=random.Random(7))
        # python has 10 questions; with 1 requested the first (least seen) is a python one
        event = load_history()[0]
        self.assertEqual(event["mode"], "qa")
        self.assertEqual(event["tag"], "python")
        self.assertIsNotNone(event["concept"])
        self.assertEqual(load_mocks()[0]["type"], "qa")

    def test_you_can_override_the_auto_grade(self):
        answers = iter(["something unrelated", "", "y"])
        run_mock_questions(1, category="git", input_fn=lambda prompt="": next(answers), out=lambda *_: None,
                           rng=random.Random(8))
        self.assertTrue(load_history()[0]["correct"])
        self.assertEqual(load_mocks()[0]["solved"], 1)

    def test_unknown_category_exits(self):
        with self.assertRaises(SystemExit):
            run_mock_questions(1, category="astrology", input_fn=lambda p="": "", out=lambda *_: None)


class CliTests(TempProgress):
    def run_cli(self, *argv):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            cli.main(list(argv))
        return buffer.getvalue()

    def test_record_updates_scores_and_history_and_scores_command_shows_it(self):
        self.run_cli("record", "--concept", "python:lists", "--result", "correct", "--difficulty", "hard")
        self.assertGreater(load_scores()["python"]["lists"]["score"], 60)
        output = self.run_cli("scores", "--history")
        self.assertIn("lists", output)
        self.assertIn("RECENT ANSWERS", output)

    def test_record_rejects_unknown_concepts(self):
        with self.assertRaises(SystemExit):
            self.run_cli("record", "--concept", "python:astrology", "--result", "correct")

    def test_record_with_a_tag_counts_toward_the_checklist(self):
        self.run_cli("record", "--tag", "git", "--qid", "claude:merge", "--result", "correct")
        self.run_cli("record", "--tag", "git", "--qid", "claude:undo", "--result", "correct")
        self.assertIn("[x] Git", self.run_cli("checklist"))

    def test_checklist_done_and_missing_views(self):
        self.run_cli("checklist", "done", "resume-walkthrough")
        missing = self.run_cli("checklist", "missing")
        self.assertNotIn("Can walk through every line", missing)
        self.assertIn("Arrays and strings", missing)

    def test_prep_new_from_text_then_show_and_list(self):
        self.run_cli("prep", "new", "demo", "--text", "Python and SQL developer, strong teamwork")
        self.assertIn("demo", self.run_cli("prep", "list"))
        self.assertIn("PREP PLAN: demo", self.run_cli("prep", "show", "demo"))

    def test_concepts_and_company_list_work_with_nothing_researched(self):
        self.assertIn("python:lists", self.run_cli("concepts"))
        self.assertIn("No company research", self.run_cli("company", "list"))

    def test_mock_history_empty(self):
        self.assertIn("No mock interviews", self.run_cli("mock", "history"))


if __name__ == "__main__":
    unittest.main()
