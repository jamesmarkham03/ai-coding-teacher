---
name: mock-interview
description: Run a realistic mock interview with Claude as the interviewer (coding round or conceptual and behavioral questions), grade it like an interviewer would, and log the results. Use when James wants a mock interview with live feedback, wants to practise talking through a problem, or runs /mock-interview.
---

The terminal tutor (`python -m tutor mock coding` / `mock questions`) gives timed, auto-graded mocks. This skill is the live version: you are the interviewer and can ask follow-ups, which the script can't.

1. **Set it up.** Ask (one message): coding round or questions round, which company or role (check `python -m tutor prep list` and `python -m tutor company list`; if a prep plan or company profile exists, use its concepts and question themes), and how long (default 30 minutes for coding, 5 questions for the questions round).

2. **Interview rules.** State them once: you will not give hints unless he asks for one (and a hint is noted), he should think out loud, and you will give feedback at the end, not during.

3. **Coding round.**
   - Give one problem at a time at the right level (use the bank's questions in `data/bank/` for the language when they fit, so results can be tested; otherwise write your own).
   - Let him ask clarifying questions. Answer them like an interviewer. Good candidates ask about input size, duplicates, empty input and what to return.
   - When he has code, run it for real against test cases (and your own edge cases) instead of eyeballing it.
   - Ask follow-ups in order: complexity, a worse case, then "how would you improve it?".
   - Score each problem: correctness, approach, communication, edge cases, complexity.

4. **Questions round.** Ask one question at a time: technical concepts (use `data/interview_questions.json` as a source, the `key_points` are the rubric) and behavioral questions (STAR). For behavioral answers, grade structure (Situation, Task, Action, Result), specificity, ownership ("I" not only "we"), and a concrete result. Coach him toward real stories from his baseball coaching and school work when they fit. Never write an answer for him to memorize; point out what is missing.

5. **Debrief.** Give a short scorecard: 3 strengths, 3 things to fix, one concrete drill for each fix, and a pass/borderline/fail call as a typical interviewer would see it. Be honest and specific. Do not inflate.

6. **Log it** so scores and the checklist update:
   - per coding problem: `python -m tutor record --concept python:graphs --result correct|wrong --difficulty medium --weight 1.25 --mode mock`
   - per questions-round answer: `python -m tutor record --tag behavioral --qid claude:<short-slug> --result correct|wrong --mode qa` (add `--concept` if it maps to a coding concept)
   Then show `python -m tutor checklist` and name the biggest uncovered area.
