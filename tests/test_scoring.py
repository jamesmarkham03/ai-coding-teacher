import unittest
from datetime import datetime, timedelta

from tests.helpers import TempProgress
from tutor.bank import load_bank
from tutor.history import load_history, log_event, seen_counts
from tutor.report import format_history, format_scores
from tutor.scoring import (START_SCORE, due_for_review, language_score, level_label, load_scores, priority,
                           record_result, save_scores, weakest_concept)

NOW = datetime(2026, 10, 29, 12, 0)


class ScoringTests(unittest.TestCase):
    def test_right_answer_moves_a_new_concept_toward_100(self):
        scores = record_result({}, "python", "lists", correct=True)
        self.assertEqual(scores["python"]["lists"]["score"], 65.0)  # 50 + 0.3 * 50
        self.assertEqual(scores["python"]["lists"]["attempts"], 1)

    def test_wrong_answer_moves_score_toward_zero(self):
        scores = record_result({}, "python", "lists", correct=False)
        self.assertEqual(scores["python"]["lists"]["score"], 35.0)

    def test_hard_questions_reward_more_and_punish_less(self):
        easy_right = record_result({}, "python", "a", True, "easy")["python"]["a"]["score"]
        hard_right = record_result({}, "python", "a", True, "hard")["python"]["a"]["score"]
        easy_wrong = record_result({}, "python", "b", False, "easy")["python"]["b"]["score"]
        hard_wrong = record_result({}, "python", "b", False, "hard")["python"]["b"]["score"]
        self.assertGreater(hard_right, easy_right)
        self.assertLess(easy_wrong, hard_wrong)

    def test_weight_scales_the_move_and_is_capped(self):
        half = record_result({}, "python", "a", True, "medium", weight=0.5)["python"]["a"]["score"]
        capped = record_result({}, "python", "a", True, "hard", weight=10)["python"]["a"]["score"]
        self.assertEqual(half, 57.5)
        self.assertEqual(capped, 80.0)  # rate capped at 0.6: 50 + 0.6 * 50

    def test_language_score_averages_tried_concepts_only(self):
        scores = {"python": {"lists": {"score": 80, "attempts": 2}, "strings": {"score": 60, "attempts": 1}}}
        self.assertEqual(language_score(scores, "python"), 70.0)
        self.assertIsNone(language_score(scores, "java"))

    def test_weakest_concept_treats_untried_as_middle(self):
        scores = {"python": {"lists": {"score": 80, "attempts": 2}}}
        self.assertEqual(weakest_concept(scores, "python", ["lists", "dictionaries", "strings"], NOW), "dictionaries")
        self.assertEqual(START_SCORE, 50)

    def test_levels(self):
        self.assertEqual([level_label(s) for s in (10, 50, 70, 90)], ["weak", "building", "solid", "strong"])

    def test_review_due_after_the_interval_passes(self):
        scores = {"python": {"lists": {"score": 50, "attempts": 1, "last_practiced": (NOW - timedelta(days=10)).isoformat()},
                             "sets": {"score": 50, "attempts": 1, "last_practiced": (NOW - timedelta(days=2)).isoformat()}}}
        due = due_for_review(scores, NOW)
        self.assertEqual([d["concept"] for d in due], ["lists"])  # interval for 50 is 6 days

    def test_overdue_concept_gets_a_priority_bonus(self):
        fresh = {"python": {"a": {"score": 50, "attempts": 1, "last_practiced": NOW.isoformat()}}}
        stale = {"python": {"a": {"score": 50, "attempts": 1, "last_practiced": (NOW - timedelta(days=30)).isoformat()}}}
        self.assertGreater(priority(stale, "python", "a", now=NOW), priority(fresh, "python", "a", now=NOW))


class PersistenceTests(TempProgress):
    def test_scores_round_trip_and_history_counts(self):
        save_scores(record_result({}, "python", "lists", True, now=NOW))
        self.assertEqual(load_scores()["python"]["lists"]["attempts"], 1)
        log_event(mode="learn", qid="q1", correct=True, now=NOW)
        log_event(mode="learn", qid="q1", correct=False, now=NOW)
        self.assertEqual(seen_counts(load_history()), {"q1": 2})

    def test_missing_files_give_empty_defaults(self):
        self.assertEqual(load_scores(), {})
        self.assertEqual(load_history(), [])

    def test_score_report_lists_languages_strongest_first(self):
        scores = {}
        record_result(scores, "sql", "joins", True, now=NOW)
        record_result(scores, "python", "lists", False, now=NOW)
        text = format_scores(scores, load_bank(), NOW)
        self.assertLess(text.index("sql "), text.index("python "))  # sql 65 beats python 35
        self.assertIn("NEXT UP", text)
        self.assertIn("No answers logged", format_history([]))


if __name__ == "__main__":
    unittest.main()
