# AI Coding Teacher

The global `CLAUDE.md` in `OS/` still applies.

## What this is
A coding tutor for James's interview prep. Each session: teach one concept, practise it with quick questions, then a LeetCode/interview-style coding question that is tested automatically. Results update per-concept and per-language scores. It also builds prep plans from job descriptions and companies, runs mock interviews, and tracks a checklist of general interview topics.

## Stack
- Python 3.12, standard library only (no installs). JavaScript questions run on Node (already installed); SQL runs on Python's sqlite3.
- Data lives in plain JSON files.

## Layout
- `tutor/cli.py`: `python -m tutor <command>`. Start here.
- `tutor/bank.py`: loads/validates `data/bank/*.json`, picks the next question (least seen, nearest difficulty).
- `tutor/runners.py` + `tutor/harness/`: run a solution against tests in a subprocess with a timeout (Python, JavaScript) or in-memory SQLite (SQL).
- `tutor/practice.py`: interactive quick/coding question prompts used by the terminal mock interviews.
- `tutor/session.py`: picks the next concept and questions (the teaching is the `/learn` skill). `tutor/scoring.py`: scores, levels, review-due. `tutor/history.py`: answer log.
- `tutor/prep.py`, `tutor/companies.py`: job description reader and company profiles. `tutor/mock.py`: mock interviews. `tutor/checklist.py`, `tutor/report.py`.
- `data/bank/` questions, `data/lessons/<language>/<concept>.md`, `data/checklist.json`, `data/taxonomy.json`, `data/interview_questions.json`, `data/companies/`.
- `progress/`: personal state (scores, history, mocks, prep plans, solutions). Git-ignored. Tests redirect it to a temp folder via `tests/helpers.py`.
- `.claude/skills/`: `learn`, `company-research`, `interview-prep`, `mock-interview`.

## Rules for this project
- Keep teaching short and in plain English; explain new terms where they appear. Lessons end with an "Interview habit".
- **Question fields:** every question has `id`, `language`, `concept`, `kind` (`quick` | `coding`), `prompt`, `difficulty` (`easy|medium|hard`).
  - `quick`: `answer` (string or list of accepted answers), optional `options` (then the answer is a letter) and `explanation`.
  - `coding` (python/javascript): `function` or `class`, `tests`, `solution`, plus `params`, `hint`, `complexity`, `unordered` (true or "outer"), `returns` ("tree"/"list"), `starter`. Test args may use `{"$tree": [...]}` or `{"$list": [...]}` (Python only; `TreeNode` and `ListNode` are provided).
  - `coding` (sql): `setup`, `expected` rows, `solution`, optional `ordered`.
  - Long text fields can be written as a list of lines.
- **Every new coding question needs a reference `solution`.** `tests/test_bank.py` runs all of them, which is how wrong test data gets caught.
- Every concept needs a lesson file, at least 2 quick questions, and (for Python and SQL) at least one coding question.
- Scoring constants live at the top of `tutor/scoring.py` (change constants, not the formulas).
- Companies: profiles must cite sources and a confidence level and pass `python -m tutor company validate`. Never invent sources.
- Use `paths.NAME` (module attribute lookup at call time), never `from tutor.paths import NAME`, so tests can redirect it.
- Never commit `progress/` or job descriptions.

## Commands
- Tests: `python -m unittest discover -s tests -t .` (about 20 seconds).
- Study: the `/learn` skill (helpers: `python -m tutor next | question | check | record`). Scores: `python -m tutor scores`. Checklist: `python -m tutor checklist`.
- Prep: `python -m tutor prep new NAME --file jd.txt --company slug`. Mock: `python -m tutor mock coding` / `mock questions`.

## Ideas not built yet
Spaced-repetition scheduling by date, more languages (Java, C++), a progress chart/HTML dashboard, more banks per concept, importing questions from a company profile's examples.
