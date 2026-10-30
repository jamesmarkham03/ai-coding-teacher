"""Company interview profiles. The company-research skill writes them; interview prep reads them.

A profile is a JSON file in data/companies/<slug>.json:
{
  "company": "Shopify", "slug": "shopify", "researched_on": "2026-10-29", "confidence": "medium",
  "sources": [{"title": "...", "url": "..."}],
  "interview_process": ["Recruiter screen", "Technical screen (live coding)", ...],
  "languages": ["python", "sql"],
  "concepts": {"python:graphs": "high", "python:dictionaries": "medium"},
  "checklist_topics": ["behavioral-stories", "system-design-basics"],
  "question_themes": [{"theme": "...", "frequency": "high", "examples": ["..."]}],
  "tips": ["..."], "notes": "what is unverified"
}
"""
import json
import re

from tutor import paths

FREQUENCY_WEIGHT = {"high": 3, "medium": 2, "low": 1}
REQUIRED = ("company", "slug", "researched_on", "sources", "concepts")


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def company_path(slug):
    return paths.COMPANIES_DIR / f"{slugify(slug)}.json"


def load_company(slug):
    path = company_path(slug)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_companies():
    if not paths.COMPANIES_DIR.exists():
        return []
    return sorted(p.stem for p in paths.COMPANIES_DIR.glob("*.json"))


def validate_company(profile, concept_keys, checklist_ids):
    """Return a list of problems (empty means the profile is good)."""
    problems = [f"missing field {name!r}" for name in REQUIRED if name not in profile]
    if not profile.get("sources"):
        problems.append("add at least one source (title + url) so the research can be checked")
    for key, frequency in profile.get("concepts", {}).items():
        if key not in concept_keys:
            problems.append(f"concept {key!r} is not in the question bank (see: python -m tutor concepts)")
        if frequency not in FREQUENCY_WEIGHT:
            problems.append(f"concept {key!r} has frequency {frequency!r}; use high, medium or low")
    for topic in profile.get("checklist_topics", []):
        if topic not in checklist_ids:
            problems.append(f"checklist topic {topic!r} is not a checklist id (see: python -m tutor checklist)")
    return problems


def format_company(profile):
    lines = [f"{profile['company']}  (researched {profile['researched_on']}, confidence {profile.get('confidence', '?')})"]
    if profile.get("interview_process"):
        lines += ["", "Interview process:"] + [f"  {i}. {step}" for i, step in enumerate(profile["interview_process"], 1)]
    if profile.get("languages"):
        lines += ["", "Languages: " + ", ".join(profile["languages"])]
    if profile.get("concepts"):
        lines += ["", "Concepts to practise:"] + [f"  {key}  ({freq})" for key, freq in profile["concepts"].items()]
    for theme in profile.get("question_themes", []):
        lines += ["", f"Theme: {theme['theme']} ({theme.get('frequency', '?')})"]
        lines += [f"  - {example}" for example in theme.get("examples", [])]
    if profile.get("tips"):
        lines += ["", "Tips:"] + [f"  - {tip}" for tip in profile["tips"]]
    if profile.get("notes"):
        lines += ["", "Notes: " + profile["notes"]]
    lines += ["", "Sources:"] + [f"  - {s.get('title', '')} {s.get('url', '')}" for s in profile.get("sources", [])]
    return "\n".join(lines)
