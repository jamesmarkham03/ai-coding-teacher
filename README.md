# AI Coding Teacher

A terminal tutor for coding-interview prep. It teaches a concept, makes you practise it, then gives you a LeetCode-style question that is tested automatically. Every answer updates a score for that concept and that language, so it always knows what you are strong and weak at.

**What's inside**
- Question bank: 153 questions, 29 concepts, in Python (20 concepts), SQL (4) and JavaScript (5). Each coding question has tests and a reference solution.
- Teach -> practice -> question sessions.
- Scores per concept and per language, spaced-review reminders.
- Interview prep from a job description or a company.
- Mock coding interviews (timed) and mock question interviews (conceptual + behavioral).
- A checklist of general interview topics showing what you have covered and what you have missed.
- Claude Code skills: `company-research`, `interview-prep`, `teach`, `mock-interview`.

## Setup
You need Python 3.12+. JavaScript questions also need Node.js (already installed if `node --version` works). SQL uses Python's built-in SQLite. No packages to install.

```bash
cd ai-coding-teacher
python -m unittest discover -s tests -t .
```
If the tests pass (they take about 20 seconds), everything works.

## Daily use
```bash
python -m tutor learn
```
Picks your weakest Python concept (or one that is due for review), shows the lesson, asks two quick questions, then a coding question. For the coding question, open the file it names under `progress/solutions/`, write your answer, save, and press Enter to run the tests. Type `hint` for a hint (the answer then counts for half) or `skip` to see one way to solve it.

| Command | What it does |
|---|---|
| `python -m tutor learn [--language sql] [--concept joins] [--review] [--prep NAME]` | A study session. `--review` refreshes the most overdue concept. |
| `python -m tutor scores [--history]` | Languages strongest first, every concept's score, what is due, what to do next. |
| `python -m tutor checklist [missing]` | General interview topics: `[x]` covered, `[~]` in progress, `[ ]` missed. |
| `python -m tutor checklist done <id>` | Mark a manual item (resume walkthrough, questions for the interviewer) as done. |
| `python -m tutor prep new NAME --file jd.txt [--company slug]` | Build a prep plan from a job description and/or researched company. |
| `python -m tutor prep show NAME` / `prep list` | Show a plan with your readiness score. |
| `python -m tutor mock coding [--prep NAME] [--minutes 30] [--count 2]` | Timed mock coding interview: no hints, complexity follow-up, scored. |
| `python -m tutor mock questions [--category behavioral] [--prep NAME]` | Mock interview of concept and behavioral questions graded against a rubric. |
| `python -m tutor company list / show slug / validate` | Researched company profiles. |
| `python -m tutor concepts` | Every concept and its question counts. |
| `python -m tutor record --concept python:lists --result correct` | Log a result from outside the tutor (the Claude skills use this). |

## How scoring works
Each concept starts at 50. A right answer moves the score toward 100, a wrong one toward 0 (30% of the gap). Hard questions move it more when you get them right, easy ones move it more when you miss them. An answer that needed a hint counts half, and mock interviews count 1.25x. A language's score is the average of the concepts you have tried, and the scores screen also shows how many of its concepts you have tried. Levels: weak (under 40), building, solid (65+), strong (85+). A concept becomes due for review after 1 + score/10 days.

## Interview prep flow
1. Ask Claude: `/company-research <company>` (saves `data/companies/<slug>.json`, validated).
2. Save the job description to a text file and run `prep new`, or ask Claude: `/interview-prep`.
3. `learn --prep NAME` until the readiness number is where you want it.
4. `mock coding --prep NAME` and `mock questions --prep NAME` as dress rehearsals.
5. `checklist` to see what is still uncovered.

## Files
- `data/` ships with the project: `bank/*.json` (questions), `lessons/`, `checklist.json`, `taxonomy.json` (keywords used to read job descriptions), `interview_questions.json`, `companies/`.
- `progress/` is yours and git-ignored: scores, history, mock records, prep plans, your solutions.

## Adding questions
Add an entry to a file in `data/bank/` (see `CLAUDE.md` for the fields) and a lesson in `data/lessons/<language>/<concept>.md` for a new concept. Include a `solution`: the test suite runs every reference solution against its own tests, so a wrong test or solution is caught immediately.

## Limits (honest list)
- Python is the deepest. SQL and JavaScript are smaller. Java, C++ and others are not supported yet; the job-description reader tells you when a role needs one.
- Mock-question grading is keyword matching against a rubric, so you get the final say (`y` / `n`). The Claude `mock-interview` skill gives richer feedback.
- Company research is only as good as public sources; every profile records its sources and a confidence level.
