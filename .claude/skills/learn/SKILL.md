---
name: learn
description: Run a study session with Claude as the teacher - teach one concept, practise it with quick questions, then a tested interview-style coding question - and log results so scores update. Use when James wants to study, learn or review a coding concept ("teach me X", "let's study", "review", "learn SQL joins"), wants to work through a prep plan, or runs /learn.
---

Run from `OS/AI/ai-coding-teacher`. The tutor commands do the bookkeeping (picking, testing, scoring). You do the teaching. Arguments after `/learn` can be a concept (`/learn joins`), `review`, or a prep plan (`/learn prep acme`); with nothing, pick the weakest.

1. **Pick the session.**
   ```
   python -m tutor next                           # weakest Python concept
   python -m tutor next --concept joins           # a named concept (any language)
   python -m tutor next --language sql            # weakest concept in a language
   python -m tutor next --review                  # most overdue concept
   python -m tutor next --prep <plan-name>        # most useful concept for a prep plan
   ```
   It prints the concept, why it was chosen, his current score, the lesson file and an ordered question list (quick ones, then one coding question). Say in one sentence what you're studying and why. If the concept has no questions yet, offer to write some (step 7).

2. **Teach it** in the style of the school bridge sets, plain English (he is learning; explain every new term the moment it appears). Read the lesson file and use it as the base, but teach it, don't paste it:
   - what it is and why it matters, in three or four sentences, with a baseball or coaching analogy only when it genuinely fits
   - one small worked example with the output shown (under 15 lines)
   - the one or two beginner mistakes
   Skip the lesson for `--review` sessions; do a 30-second refresher instead.

3. **Practise.** For each quick question in order: run `python -m tutor question <id>` and show it in your own words (don't reveal the answer). Wait for his reply, then `python -m tutor check <id> --answer "<his answer>"`. If it's wrong, give a nudge (not the answer) and let him try once more; then `--reveal`. Explain in his terms why the right answer is right.
   Offer small variations ("what if the index were -2?") when he gets one right quickly; the reps are the point.

4. **The coding question.** `python -m tutor question <id>` prints the prompt and creates a solution file under `progress/solutions/`. Tell him the file path and let him write it himself (he can edit the file, or paste code in chat and you save it there). Then:
   ```
   python -m tutor check <id>          # runs the tests on the solution file
   python -m tutor question <id> --hint   # only when he asks, or is stuck after two tries
   python -m tutor check <id> --reveal    # after he passes, or gives up
   ```
   - Review failing output with him: which input failed, what he expected vs got. Make him find the bug.
   - After it passes, ask for the time and space complexity before showing the typical complexity, then talk about one improvement or edge case. This is the interview habit.
   - If he gives up, show the reference solution and walk through it, then ask him to re-solve a variant in his own words.

5. **Log every graded question** (be honest; inflating scores defeats the purpose). One call each, using the question's own id and difficulty:
   ```
   python -m tutor record --concept python:lists --qid <id> --result correct --difficulty easy
   python -m tutor record --concept python:lists --qid <id> --result wrong --difficulty easy
   ```
   Add `--weight 0.5` for an answer that needed a hint or a second try. Use `--mode review` for review sessions.

6. **Wrap up.** Run `python -m tutor scores` and summarize in two lines: what moved and what's next. If the checklist gained something, mention it (`python -m tutor checklist`). Suggest the next concept from the "NEXT UP" line. Do not start another session unless he asks.

7. **Topics not in the bank.** If the concept has no questions or lesson, teach it live and write your own practice, and log with `--tag`/`--qid claude:<slug>` only for checklist question topics. Offer to add proper bank entries (`data/bank/`, `data/lessons/`, each coding question with a reference `solution`), then run `python -m unittest discover -s tests -t .`.

Keep a conversational pace: one question at a time, wait for his answer, short messages. If he wants to just drill with tests and no explanation, skip step 2 and go straight to the questions.
