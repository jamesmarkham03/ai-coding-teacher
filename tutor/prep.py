"""Interview prep mode: turn a job description (and/or a company profile) into a study plan.

The plan lists which concepts matter for the role, weighted by how often the job description
mentions them. It is saved in progress/prep/<name>.json and can drive the /learn skill (`next --prep`) and `mock --prep`.
"""
import json
import re
from datetime import datetime

from tutor import paths
from tutor.bank import concepts_for, split_key
from tutor.companies import FREQUENCY_WEIGHT, load_company, slugify
from tutor.scoring import concept_score, level_label
from tutor.storage import read_json, write_json

MAX_HIT_BONUS = 3  # a keyword mentioned 10 times counts as 3, so one repeated word can't dominate


def load_taxonomy():
    return json.loads(paths.TAXONOMY_PATH.read_text(encoding="utf-8"))


def keyword_hits(text, keywords):
    """Count keyword matches. A keyword must start at a word boundary, so 'rest' won't match 'interest'."""
    total = 0
    for keyword in keywords:
        total += len(re.findall(r"(?<![a-z0-9])" + re.escape(keyword), text))
    return total


def analyze_text(text, taxonomy=None):
    """Read a job description and report which languages, topics, concepts and checklist items it points to."""
    taxonomy = taxonomy or load_taxonomy()
    lowered = " " + text.lower() + " "

    languages = {}
    for language, keywords in taxonomy["languages"].items():
        hits = keyword_hits(lowered, keywords)
        if hits:
            languages[language] = hits
    unsupported = [name for name, keywords in taxonomy["unsupported_languages"].items()
                   if keyword_hits(lowered, keywords)]

    concepts, topics, checklist = {}, [], []
    for language, hits in languages.items():
        for key, weight in taxonomy["language_basics"].get(language, {}).items():
            concepts[key] = concepts.get(key, 0) + weight * min(hits, MAX_HIT_BONUS)
    for topic in taxonomy["topics"]:
        hits = keyword_hits(lowered, topic["keywords"])
        if not hits:
            continue
        topics.append(topic["id"])
        for key, weight in topic["concepts"].items():
            concepts[key] = concepts.get(key, 0) + weight * min(hits, MAX_HIT_BONUS)
        checklist += [c for c in topic.get("checklist", []) if c not in checklist]

    # A job description that mentions nothing we know still gets the classic coding-interview plan.
    if not concepts:
        dsa = next(t for t in taxonomy["topics"] if t["id"] == "dsa")
        concepts = dict(dsa["concepts"])
        topics.append("dsa (default)")
        languages = languages or {"python": 1}
    return {"languages": languages, "unsupported": unsupported, "topics": topics,
            "concepts": concepts, "checklist": checklist}


def apply_company(plan, profile):
    """Add a company's known question themes on top of the job-description analysis."""
    for key, frequency in profile.get("concepts", {}).items():
        plan["concepts"][key] = plan["concepts"].get(key, 0) + FREQUENCY_WEIGHT[frequency]
    for language in profile.get("languages", []):
        plan["languages"][language] = plan["languages"].get(language, 0) + 2
    for item in profile.get("checklist_topics", []):
        if item not in plan["checklist"]:
            plan["checklist"].append(item)
    plan["company"] = profile["slug"]
    return plan


def prep_path(name):
    return paths.PREP_DIR / f"{slugify(name)}.json"


def create_prep(name, text="", company=None, taxonomy=None):
    """Build and save a prep plan from job-description text and/or a company profile."""
    if not text.strip() and not company:
        raise SystemExit("Give me a job description (--file or --text) or a company (--company).")
    plan = analyze_text(text, taxonomy) if text.strip() else {
        "languages": {}, "unsupported": [], "topics": [], "concepts": {}, "checklist": []}
    plan.update({"name": slugify(name), "created": datetime.now().isoformat(timespec="seconds"),
                 "company": None, "excerpt": " ".join(text.split())[:300]})
    if company:
        profile = load_company(company)
        if profile is None:
            plan["company_missing"] = company
        else:
            apply_company(plan, profile)
    if not plan["concepts"]:
        defaults = analyze_text("", taxonomy)
        plan["concepts"] = defaults["concepts"]
        plan["topics"] = plan["topics"] + defaults["topics"]
        plan["languages"] = plan["languages"] or defaults["languages"]
    plan["concepts"] = {k: min(v, 8) for k, v in plan["concepts"].items()}
    write_json(prep_path(name), plan)
    return plan


def load_prep(name):
    plan = read_json(prep_path(name), None)
    if plan is None:
        raise SystemExit(f"No prep plan called {name!r}. Run: python -m tutor prep list")
    return plan


def list_preps():
    if not paths.PREP_DIR.exists():
        return []
    return sorted(p.stem for p in paths.PREP_DIR.glob("*.json"))


def readiness(plan, scores, bank):
    """Weighted average score over the plan's concepts that the bank can actually teach (0-100)."""
    total = weight_sum = 0
    for key, weight in plan["concepts"].items():
        language, concept = split_key(key)
        if concept in concepts_for(bank, language):
            total += weight * concept_score(scores, language, concept)
            weight_sum += weight
    return round(total / weight_sum, 1) if weight_sum else 0.0


def format_plan(plan, scores, bank):
    lines = [f"PREP PLAN: {plan['name']}"]
    if plan.get("company"):
        lines.append(f"Company profile: {plan['company']}")
    if plan.get("company_missing"):
        lines.append(f"No research found for {plan['company_missing']!r} yet. Run the company-research skill "
                     f"(/company-research {plan['company_missing']}) and re-run prep with --company.")
    if plan["languages"]:
        langs = ", ".join(f"{l} (x{n})" for l, n in sorted(plan["languages"].items(), key=lambda i: -i[1]))
        lines.append(f"Languages: {langs}")
    if plan["unsupported"]:
        lines.append("Not supported by this tutor yet: " + ", ".join(plan["unsupported"])
                     + ". The algorithm and data-structure practice still carries over.")
    if plan["topics"]:
        lines.append("Topics detected: " + ", ".join(plan["topics"]))
    lines.append(f"Readiness: {readiness(plan, scores, bank)}/100")

    lines += ["", f"  {'concept':<32}{'weight':>6}{'score':>7}  level"]
    ranked = sorted(plan["concepts"].items(), key=lambda i: (-i[1], i[0]))
    teachable = 0
    for key, weight in ranked:
        language, concept = split_key(key)
        if concept not in concepts_for(bank, language):
            lines.append(f"  {key:<32}{weight:>6}{'--':>7}  (no questions yet)")
            continue
        teachable += 1
        score = concept_score(scores, language, concept)
        lines.append(f"  {key:<32}{weight:>6}{score:>7}  {level_label(score)}")
    if plan["checklist"]:
        lines += ["", "Also prepare (checklist): " + ", ".join(plan["checklist"])]
    lines += ["", f"Study it:   /learn with prep plan {plan['name']}  (in Claude Code)",
              f"Mock it:    python -m tutor mock coding --prep {plan['name']}",
              f"            python -m tutor mock questions --prep {plan['name']}"]
    return "\n".join(lines)
