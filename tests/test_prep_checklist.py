import json
import unittest

from tests.helpers import TempProgress
from tutor import checklist, companies, paths
from tutor.bank import all_concept_keys, load_bank
from tutor.history import log_event
from tutor.prep import analyze_text, create_prep, format_plan, list_preps, load_prep, readiness
from tutor.scoring import record_result

JD = """Data Analyst Intern. You will write SQL queries (joins, aggregation, window functions) against our
Postgres warehouse and build dashboards. Python (pandas) for ETL pipelines. Strong communication and teamwork.
Nice to have: Java, Git, unit testing."""


class AnalyzeTests(unittest.TestCase):
    def test_job_description_maps_to_languages_concepts_and_checklist(self):
        found = analyze_text(JD)
        self.assertIn("sql", found["languages"])
        self.assertIn("python", found["languages"])
        self.assertEqual(found["unsupported"], ["java"])
        self.assertGreater(found["concepts"]["sql:aggregation"], found["concepts"]["sql:select-filter"])
        self.assertIn("behavioral-stories", found["checklist"])
        self.assertIn("git", found["checklist"])

    def test_keywords_match_at_word_starts_only(self):
        self.assertNotIn("apis-web", analyze_text("We value interest in forests")["topics"])

    def test_unrecognised_text_falls_back_to_the_classic_coding_plan(self):
        found = analyze_text("Looking for a keen person.")
        self.assertIn("python:graphs", found["concepts"])
        self.assertIn("dsa (default)", found["topics"])

    def test_algorithm_roles_pull_in_data_structure_concepts(self):
        found = analyze_text("Strong data structures and algorithms, dynamic programming, Java or C++")
        self.assertGreater(found["concepts"]["python:dynamic-programming"], 2)
        self.assertEqual(set(found["unsupported"]), {"java", "c++"})


class PrepPlanTests(TempProgress):
    def setUp(self):
        super().setUp()
        self.bank = load_bank()

    def test_create_save_load_and_list(self):
        plan = create_prep("Acme Intern", JD)
        self.assertEqual(plan["name"], "acme-intern")
        self.assertEqual(list_preps(), ["acme-intern"])
        self.assertEqual(load_prep("acme-intern")["concepts"], plan["concepts"])

    def test_readiness_rises_when_target_concepts_improve(self):
        plan = create_prep("acme", JD)
        before = readiness(plan, {}, self.bank)
        scores = {}
        for key in plan["concepts"]:
            language, concept = key.split(":")
            record_result(scores, language, concept, True, "hard")
        self.assertGreater(readiness(plan, scores, self.bank), before)

    def test_company_profile_boosts_its_concepts(self):
        paths.COMPANIES_DIR.mkdir(parents=True)
        profile = {"company": "Acme", "slug": "acme", "researched_on": "2026-10-29", "sources": [{"title": "t", "url": "u"}],
                   "concepts": {"python:graphs": "high"}, "languages": ["python"], "checklist_topics": ["system-design-basics"]}
        (paths.COMPANIES_DIR / "acme.json").write_text(json.dumps(profile), encoding="utf-8")
        plan = create_prep("acme-prep", "Backend role using Python.", company="acme")
        self.assertGreaterEqual(plan["concepts"]["python:graphs"], 3)
        self.assertEqual(plan["company"], "acme")
        self.assertIn("system-design-basics", plan["checklist"])

    def test_unknown_company_is_noted_not_fatal(self):
        plan = create_prep("x", "Python developer", company="nobody")
        self.assertEqual(plan["company_missing"], "nobody")
        self.assertIn("company-research", format_plan(plan, {}, self.bank))

    def test_company_only_prep_without_a_job_description(self):
        paths.COMPANIES_DIR.mkdir(parents=True)
        profile = {"company": "Beta", "slug": "beta", "researched_on": "2026-10-29", "sources": [{"title": "t", "url": "u"}],
                   "concepts": {"sql:joins": "medium"}}
        (paths.COMPANIES_DIR / "beta.json").write_text(json.dumps(profile), encoding="utf-8")
        self.assertEqual(create_prep("beta", "", company="beta")["concepts"], {"sql:joins": 2})

    def test_nothing_to_go_on_exits(self):
        with self.assertRaises(SystemExit):
            create_prep("empty", "")

    def test_plan_text_flags_unsupported_and_missing_questions(self):
        text = format_plan(create_prep("acme", JD), {}, self.bank)
        self.assertIn("Not supported by this tutor yet: java", text)
        self.assertIn("python -m tutor learn --prep acme", text)

    def test_load_missing_plan_exits(self):
        with self.assertRaises(SystemExit):
            load_prep("ghost")


class CompanyValidationTests(unittest.TestCase):
    def test_validation_catches_bad_concepts_missing_sources_and_bad_frequency(self):
        keys = set(all_concept_keys(load_bank()))
        ids = {i["id"] for i in checklist.load_checklist()}
        good = {"company": "A", "slug": "a", "researched_on": "2026-01-01", "sources": [{"title": "t", "url": "u"}],
                "concepts": {"python:graphs": "high"}}
        self.assertEqual(companies.validate_company(good, keys, ids), [])
        bad = {"company": "A", "slug": "a", "researched_on": "2026-01-01", "sources": [],
               "concepts": {"python:nope": "high", "python:graphs": "huge"}, "checklist_topics": ["nope"]}
        problems = " | ".join(companies.validate_company(bad, keys, ids))
        for expected in ("source", "python:nope", "huge", "checklist topic"):
            self.assertIn(expected, problems)

    def test_slugify(self):
        self.assertEqual(companies.slugify("Shopify Inc."), "shopify-inc")


class ChecklistTests(TempProgress):
    def report(self, mocks=(), preps=0):
        from tutor.history import load_history
        from tutor.scoring import load_scores
        return {i["id"]: (s, d) for i, s, d in checklist.checklist_report(load_scores(), load_history(), list(mocks), preps)}

    def test_everything_starts_missed(self):
        self.assertTrue(all(status == "missed" for status, _ in self.report().values()))

    def test_concept_items_go_missed_started_covered(self):
        from tutor.scoring import save_scores
        scores = record_result({}, "python", "lists", True, "hard")
        save_scores(scores)
        self.assertEqual(self.report()["arrays-strings"][0], "started")  # strings not tried yet
        scores = record_result(scores, "python", "strings", True, "hard")
        record_result(scores, "python", "lists", True, "hard")
        save_scores(scores)
        self.assertEqual(self.report()["arrays-strings"][0], "covered")

    def test_question_items_need_enough_distinct_good_answers(self):
        log_event(mode="qa", tag="git", qid="a", correct=True)
        log_event(mode="qa", tag="git", qid="a", correct=True)  # same question twice doesn't double count
        self.assertEqual(self.report()["git"][0], "started")
        log_event(mode="qa", tag="git", qid="b", correct=True)
        self.assertEqual(self.report()["git"][0], "covered")

    def test_missed_answers_do_not_count_as_covered(self):
        log_event(mode="qa", tag="git", qid="a", correct=False)
        log_event(mode="qa", tag="git", qid="b", correct=False)
        self.assertEqual(self.report()["git"][0], "started")

    def test_manual_items_and_undo(self):
        self.assertEqual(self.report()["resume-walkthrough"][0], "missed")
        checklist.set_done("resume-walkthrough")
        self.assertEqual(self.report()["resume-walkthrough"][0], "covered")
        checklist.set_done("resume-walkthrough", False)
        self.assertEqual(self.report()["resume-walkthrough"][0], "missed")
        with self.assertRaises(SystemExit):
            checklist.set_done("no-such-item")

    def test_mock_and_prep_items_count_automatically(self):
        report = self.report(mocks=[{"type": "coding"}], preps=1)
        self.assertEqual(report["think-aloud"][0], "covered")
        self.assertEqual(report["mock-coding-reps"][0], "started")
        self.assertEqual(report["target-role-prep"][0], "covered")

    def test_checklist_references_only_real_concepts_and_formats(self):
        keys = set(all_concept_keys(load_bank()))
        for item in checklist.load_checklist():
            for key in item.get("concepts", []):
                self.assertIn(key, keys, item["id"])
        text = checklist.format_checklist(checklist.checklist_report({}, [], [], 0), only_missing=True)
        self.assertIn("0/", text)
        self.assertIn("CODING FUNDAMENTALS", text)


if __name__ == "__main__":
    unittest.main()
