"""Every file location in one place.

Modules read these as `paths.NAME` at call time (not `from paths import NAME`), so tests can
point them at a temporary folder.

data/      content that ships with the project (questions, lessons, checklist, company research)
progress/  personal state (scores, history, answers, prep plans). Git-ignored.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA = ROOT / "data"
BANK_DIR = DATA / "bank"
LESSONS_DIR = DATA / "lessons"
COMPANIES_DIR = DATA / "companies"
CHECKLIST_PATH = DATA / "checklist.json"
TAXONOMY_PATH = DATA / "taxonomy.json"
INTERVIEW_QA_PATH = DATA / "interview_questions.json"

PROGRESS = ROOT / "progress"
SCORES_PATH = PROGRESS / "scores.json"
HISTORY_PATH = PROGRESS / "history.json"
MOCKS_PATH = PROGRESS / "mocks.json"
CHECKLIST_STATE_PATH = PROGRESS / "checklist_state.json"
PREP_DIR = PROGRESS / "prep"
SOLUTIONS_DIR = PROGRESS / "solutions"
