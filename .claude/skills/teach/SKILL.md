---
name: teach
description: Teach a coding concept live in conversation (teach, practice, then an interview-style question) and log the result to the tutor's scores. Use when James wants to learn or review a concept with Claude explaining it, asks "teach me X", wants a topic that is not in the question bank, or runs /teach.
---

This is the conversational version of `python -m tutor learn`. Use the terminal tutor when he wants timed, automatically tested practice. Use this skill when he wants explanations, a topic outside the bank, or help while stuck.

1. **Pick the concept.** If he named one, use it. Otherwise run `python -m tutor scores` and take the "NEXT UP" line (or `python -m tutor concepts` to list names). Say which concept and why in one sentence.

2. **Teach it** in the style of the school bridge sets, in plain English (he is learning; explain new terms the moment they appear):
   - What it is and why it matters, in three or four sentences, with one baseball or coaching analogy only when it truly fits.
   - A small worked example with the output shown. Keep it under 15 lines of code.
   - The one or two mistakes beginners make with it.
   Reuse the lesson in `data/lessons/<language>/<concept>.md` as the base if it exists, but explain it fresh; don't paste it.

3. **Practice (2 to 3 small reps).** Ask one question at a time and wait. Mix a predict-the-output question and a "write a tiny function" question. After each answer, say what was right, name the exact misunderstanding if wrong, and let him retry once before explaining. Do not give the answer away if he is close. He learns from reps and mistakes.

4. **Interview question.** Give one LeetCode-style or interview-style question at the right level (easy if his score on the concept is under about 55, medium under 78, otherwise hard). Let him write a solution in chat or a file, then check it by actually running it with the tests when possible. Ask for the time and space complexity. Give feedback like an interviewer: correctness, edge cases, complexity, clarity.

5. **Log the result** so the scores update. One call per question graded:
   ```
   python -m tutor record --concept python:lists --result correct --difficulty medium
   python -m tutor record --concept python:lists --result wrong --difficulty easy
   ```
   Use `--weight 0.5` for an answer that needed a lot of hints. For free-form interview-style questions that belong to the checklist (behavioral, system design, databases...) add `--tag <tag> --qid claude:<short-unique-slug>`.
   Only log what he really attempted, and log honestly; inflating a score defeats the purpose.

6. **Wrap up** with `python -m tutor scores` output summarized in two lines: what moved, and the next concept. If the bank has no lesson or questions for this concept, offer to write them into `data/bank/` and `data/lessons/` (run `python -m unittest discover -s tests -t .` afterwards, since the tests check every reference solution).
