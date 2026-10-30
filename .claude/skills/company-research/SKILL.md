---
name: company-research
description: Research what kinds of coding and interview questions a company usually asks, then save a validated profile the tutor uses for interview prep. Use when James names a company he is interviewing with or applying to, asks "what does X ask in interviews", or runs /company-research.
---

Goal: produce `data/companies/<slug>.json` that `python -m tutor prep new <name> --company <slug>` can use to weight his practice.

1. **Check what exists.** Run `python -m tutor company list`. If a profile for this company exists and `researched_on` is under 90 days old, show it (`python -m tutor company show <slug>`) and ask whether to refresh before researching again.

2. **Find the role.** If James gave a job posting or role, use it (software intern, data analyst, ML, etc.). If not, ask once which role and level, because question types differ a lot between a data analyst and a backend engineer.

3. **Research with the `researcher` agent or web search.** Public sources only. Look for, in this order of trust:
   - the company's own careers/interview-process pages and engineering blog (official)
   - candidate write-ups: Glassdoor interview reviews, Blind, Reddit (r/cscareerquestions, r/leetcode), LeetCode Discuss "interview experience" posts, personal blogs
   - Search ideas: `"<company> interview process <role>"`, `"<company> new grad / intern coding interview questions"`, `"<company> leetcode interview experience"`.
   Gather: the stages of the process, what the coding rounds cover (data structures, SQL, take-home, pair programming), languages allowed, behavioral/values emphasis, system design expectations, and any specific problems candidates report.

4. **Map findings to the tutor's concepts.** Run `python -m tutor concepts` and `python -m tutor checklist` for valid names. Only use concept keys from that list (`python:graphs`, `sql:joins`, ...) and checklist ids. Rate each concept `high` (several independent reports), `medium` (one or two reports or implied by the role), or `low` (guess from the job posting). Never invent a concept key.

5. **Write the profile** to `data/companies/<slug>.json` (slug = lowercase, hyphens). Schema:
   ```json
   {
     "company": "Name", "slug": "name", "researched_on": "YYYY-MM-DD", "role": "role researched",
     "confidence": "low | medium | high",
     "sources": [{"title": "...", "url": "..."}],
     "interview_process": ["Recruiter screen (30 min)", "..."],
     "languages": ["python", "sql"],
     "concepts": {"python:graphs": "high", "sql:joins": "medium"},
     "checklist_topics": ["behavioral-stories", "system-design-basics"],
     "question_themes": [{"theme": "...", "frequency": "high", "examples": ["short paraphrase"]}],
     "tips": ["..."],
     "notes": "what is unverified or conflicting"
   }
   ```
   Rules:
   - Paraphrase. Do not copy long passages or paste whole interview questions from copyrighted sites; short paraphrased examples are fine.
   - `confidence`: `high` only with an official source plus two or more independent candidate reports; `low` if it mostly rests on the job posting or a single anecdote.
   - Put anything unconfirmed or contradictory in `notes`. Candidate reports can be old, so mention the year when a source is dated.
   - Never fabricate sources or URLs. If you could not find solid information, say so, set `confidence: "low"` and base `concepts` on the posting.

6. **Validate.** Run `python -m tutor company validate <slug>`. Fix every problem it lists, then validate again.

7. **Report back, short:** the process in one line, the top 3 to 5 concepts to practise and why, the confidence level, and the next step: `python -m tutor prep new <name> --file <job-description.txt> --company <slug>`. Offer to run `/interview-prep`.

If James asks you to research a company where the question is about a private person or non-public information, decline that part; this skill is for public interview-process information only.
