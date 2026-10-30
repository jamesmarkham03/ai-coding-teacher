---
name: interview-prep
description: Build a targeted interview prep plan from a job description and/or company, then start working through it. Use when James pastes a job posting, names a role or company he is interviewing for, or runs /interview-prep.
---

1. **Get the inputs.** A job description (pasted text or a file path) and/or a company name. If he only gave a company, still go on; the company profile alone can drive the plan.

2. **Save the job description** to a file inside `progress/` (it is git-ignored), for example `progress/jd-<company>-<role>.txt`. Do not commit job descriptions.

3. **Research the company** if there is no profile yet: run `python -m tutor company list`. If missing, follow the `company-research` skill first. Then you will have `data/companies/<slug>.json`.

4. **Create the plan:**
   ```
   python -m tutor prep new <name> --file progress/jd-<company>-<role>.txt --company <slug>
   ```
   Leave out `--company` or `--file` if you don't have them. Read the output back to James in plain English:
   - which languages and topics the role points to (and any unsupported language, such as Java, where the data-structure practice still carries over)
   - the top concepts to practise and his current score on each
   - his readiness number, and what the plan will do to raise it

5. **Check gaps the tutor can't cover yet.** If the role needs something the bank has no questions for (a language like Java, a framework), say so plainly and suggest the closest practice (same algorithms in Python). Offer to add questions to `data/bank/` if it is worth it.

6. **Propose a schedule** that fits his hours (he has at least 10 hours a week for projects, less in baseball season): for example 3 `learn --prep` sessions, one `mock coding --prep`, one `mock questions --prep` per week until the interview date. Ask for the interview date if he has one, and work backward.

7. **Start now:** offer to run the first session: `python -m tutor learn --prep <name>`. Remind him `python -m tutor checklist` shows what is still uncovered.

Keep it short and concrete. Don't promise the plan will cover everything the interviewer asks; say that it targets the most likely areas.
