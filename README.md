# AI Coding Teacher

A terminal tutor for coding interview prep. It teaches one concept, checks you with a quick question, then gives you a LeetCode-style coding problem. Your results are saved per concept and per language, so the tutor can show where you are strong and where you need work.

## Setup
You need Python 3.12 or newer. No packages to install.

```bash
cd ai-coding-teacher
python -m unittest discover -s tests
```

If the tests pass, the project is ready.

## Run a session
```bash
python -m tutor.session
```
This picks your weakest Python concept. To choose one yourself:
```bash
python -m tutor.session --concept dictionaries
```

Each session:
1. Reads the lesson for the concept.
2. Asks a quick question. Type your answer and press Enter.
3. Opens a coding question. Write your code in the file it names under `solutions/`, save it, then press Enter. The tutor runs your code against test cases.
4. Saves your results to `data/scores.json`.

## See your scores
```bash
python -m tutor.show_scores
```

## Adding questions
Add an entry to `data/question_bank.json`. See the rules in `CLAUDE.md`.
