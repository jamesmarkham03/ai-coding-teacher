"""The general interview-topics checklist: what you've covered and what you've missed.

Statuses:  covered  [x]   in progress  [~]   missed  [ ]
How an item is judged:
  concepts  -> every listed concept has been tried and their average score is at least COVER_SCORE
  qa        -> at least `need` different interview questions with that tag answered well
  auto      -> counted from mock interviews or prep plans
  manual    -> you mark it done yourself:  python -m tutor checklist done <id>
"""
import json

from tutor import paths
from tutor.storage import read_json, write_json

COVER_SCORE = 65


def load_checklist():
    return json.loads(paths.CHECKLIST_PATH.read_text(encoding="utf-8"))


def load_state():
    return read_json(paths.CHECKLIST_STATE_PATH, {"done": []})


def set_done(item_id, done=True):
    ids = {item["id"] for item in load_checklist()}
    if item_id not in ids:
        raise SystemExit(f"Unknown checklist item {item_id!r}. Run: python -m tutor checklist")
    state = load_state()
    done_ids = set(state["done"])
    done_ids.add(item_id) if done else done_ids.discard(item_id)
    state["done"] = sorted(done_ids)
    write_json(paths.CHECKLIST_STATE_PATH, state)


def qa_passed(history, tag):
    """(distinct questions answered well, distinct questions tried) for one interview-question tag."""
    passed, tried = set(), set()
    for event in history:
        if event.get("tag") == tag and event.get("qid"):
            tried.add(event["qid"])
            if event.get("correct"):
                passed.add(event["qid"])
    return len(passed), len(tried)


def item_status(item, scores, history, mocks, prep_count, state):
    """Return (status, detail) for one checklist item."""
    if item["id"] in state["done"]:
        return "covered", "marked done"

    if "concepts" in item:
        entries = []
        for key in item["concepts"]:
            language, concept = key.split(":", 1)
            entries.append(scores.get(language, {}).get(concept))
        tried = [e for e in entries if e]
        if not tried:
            return "missed", f"0/{len(entries)} concepts tried"
        average = sum(e["score"] for e in tried) / len(tried)
        if len(tried) == len(entries) and average >= COVER_SCORE:
            return "covered", f"average score {average:.0f}"
        return "started", f"{len(tried)}/{len(entries)} tried, average {average:.0f} (need {COVER_SCORE})"

    if "qa" in item:
        passed, tried = qa_passed(history, item["qa"])
        need = item.get("need", 2)
        if passed >= need:
            return "covered", f"{passed} questions answered well"
        if tried:
            return "started", f"{passed}/{need} answered well ({tried} tried)"
        return "missed", f"0/{need} questions answered (python -m tutor mock questions --category {item['qa']})"

    if "auto" in item:
        kind = item["auto"]
        if kind == "prep":
            count = prep_count
        else:
            count = sum(1 for m in mocks if m["type"] == kind.replace("mock-", ""))
        need = item.get("need", 1)
        if count >= need:
            return "covered", f"{count} done"
        return ("started" if count else "missed"), f"{count}/{need} done"

    return "missed", "mark with: python -m tutor checklist done " + item["id"]


def checklist_report(scores, history, mocks, prep_count):
    """List of (item, status, detail) in checklist order."""
    state = load_state()
    return [(item, *item_status(item, scores, history, mocks, prep_count, state)) for item in load_checklist()]


def format_checklist(report, only_missing=False):
    symbols = {"covered": "[x]", "started": "[~]", "missed": "[ ]"}
    lines = []
    covered = sum(1 for _, status, _ in report if status == "covered")
    lines.append(f"INTERVIEW CHECKLIST: {covered}/{len(report)} covered   ([x] covered  [~] in progress  [ ] missed)")
    group = None
    for item, status, detail in report:
        if only_missing and status == "covered":
            continue
        if item["group"] != group:
            group = item["group"]
            lines += ["", group.upper()]
        lines.append(f"  {symbols[status]} {item['title']}  -  {detail}")
    missed = [item["title"] for item, status, _ in report if status == "missed"]
    if missed:
        lines += ["", f"Not started yet ({len(missed)}): " + "; ".join(missed[:6]) + ("..." if len(missed) > 6 else "")]
    return "\n".join(lines)
