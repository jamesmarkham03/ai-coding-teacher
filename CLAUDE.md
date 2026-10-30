# AI Coding Teacher

The global `CLAUDE.md` in `OS/` still applies.

## What this is
A coding tutor for James's interview prep. Each session: teach one concept, check it with a quick question, then give a coding question (LeetCode style). Results update a per-concept score, so the tutor knows what is strong and weak per language.

## Stack
- Python 3.12, standard library only (no installs needed).
- Data lives in plain JSON files in `data/`.

## Layout
- `tutor/bank.py`: loads and validates the question bank.
- `tutor/scoring.py`: per-concept scores, language averages, weakest concept.
- `tutor/session.py`: the teach → practice → question loop (run this).
- `tutor/show_scores.py`: prints per-concept scores.
- `data/question_bank.json`: all questions, tagged by language and concept.
- `data/lessons/<language>/<concept>.md`: the teaching text for each concept.
- `data/scores.json`: personal progress (git-ignored).
- `solutions/`: James's coding answers, one file per question (git-ignored).
- `tests/`: unit tests for the bank and scoring.

## Rules for this project
- Keep the teaching short and in plain English. Explain new terms when they appear.
- Each question in the bank needs `id`, `language`, `concept`, `kind` (`quick` or `coding`) and `prompt`. Quick questions need `answer`. Coding questions need `function` and `tests`.
- Scores move with an exponential average (`LEARNING_RATE` in `tutor/scoring.py`). Change the constant, not the formula, when tuning.
- Python first. Other languages come later as new folders in `data/lessons/` plus bank entries.
- Never commit `data/scores.json` or `solutions/`.

## Commands
- Run a session: `python -m tutor.session` (picks your weakest Python concept), or `python -m tutor.session --concept dictionaries`.
- See scores: `python -m tutor.show_scores`.
- Tests: `python -m unittest discover -s tests`.
