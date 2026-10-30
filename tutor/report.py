"""Turns scores and history into readable text (the "which concepts and languages am I strong in" view)."""
from datetime import datetime

from tutor.bank import concepts_for, languages_in
from tutor.scoring import (START_SCORE, days_since, due_for_review, language_score, level_label,
                           priority)


def bar(score, width=10):
    filled = round(score / 100 * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def ago(days):
    if days is None:
        return "never"
    if days < 1:
        return "today"
    return f"{int(days)} day{'s' if int(days) != 1 else ''} ago"


def format_scores(scores, bank, now=None):
    """The main score screen: languages strongest first, then every concept weakest first."""
    now = now or datetime.now()
    languages = languages_in(bank)
    lines = ["LANGUAGES (strongest first)"]

    def lang_sort(lang):
        value = language_score(scores, lang)
        return -(value if value is not None else -1)

    for lang in sorted(languages, key=lang_sort):
        concepts = concepts_for(bank, lang)
        tried = [c for c in concepts if c in scores.get(lang, {})]
        avg = language_score(scores, lang)
        if avg is None:
            lines.append(f"  {lang:<12}{'--':>6}  {bar(0)}  not started   0/{len(concepts)} concepts tried")
        else:
            lines.append(f"  {lang:<12}{avg:>6}  {bar(avg)}  {level_label(avg):<12}"
                         f"{len(tried)}/{len(concepts)} concepts tried")

    for lang in languages:
        lines += ["", lang.upper(), f"  {'concept':<24}{'score':>6}  {'level':<10}{'tries':>5}  last practiced"]
        entries = scores.get(lang, {})
        concepts = concepts_for(bank, lang)
        tried = sorted((c for c in concepts if c in entries), key=lambda c: entries[c]["score"])
        for concept in tried:
            entry = entries[concept]
            lines.append(f"  {concept:<24}{entry['score']:>6}  {level_label(entry['score']):<10}"
                         f"{entry['attempts']:>5}  {ago(days_since(entry, now))}")
        for concept in concepts:
            if concept not in entries:
                lines.append(f"  {concept:<24}{'--':>6}  {'new':<10}{0:>5}  never")

    due = due_for_review(scores, now)
    if due:
        lines += ["", "DUE FOR REVIEW (python -m tutor learn --review)"]
        lines += [f"  {d['language']}:{d['concept']}  (score {d['score']}, {d['days_since']} days since last practice)"
                  for d in due[:5]]
    lines += ["", "NEXT UP: " + next_up(scores, bank, now)]
    return "\n".join(lines)


def next_up(scores, bank, now=None):
    now = now or datetime.now()
    best = max(((lang, c) for lang in languages_in(bank) for c in concepts_for(bank, lang)),
               key=lambda pair: priority(scores, pair[0], pair[1], now=now))
    return f"{best[0]}:{best[1]}  (python -m tutor learn --language {best[0]} --concept {best[1]})"


def format_history(history, limit=15):
    if not history:
        return "No answers logged yet."
    lines = ["RECENT ANSWERS"]
    for event in history[-limit:][::-1]:
        mark = "right" if event.get("correct") else "miss "
        target = event.get("concept") or event.get("tag") or "-"
        lines.append(f"  {event['ts'][:16]}  {mark}  {event.get('mode', ''):<7} "
                     f"{event.get('language', ''):<11}{target:<22}{event.get('qid', '')}")
    return "\n".join(lines)


def untried_count(scores, bank):
    return sum(1 for lang in languages_in(bank) for c in concepts_for(bank, lang) if c not in scores.get(lang, {}))
