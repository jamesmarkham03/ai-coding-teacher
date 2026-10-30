"""An append-only log of every answer. Scores are a summary; this is the full record.

Each event: {"ts", "mode", "language", "concept", "qid", "correct", ...}.
mode is one of: learn, review, mock, qa, record.
"""
from datetime import datetime

from tutor import paths
from tutor.storage import read_json, write_json


def load_history():
    return read_json(paths.HISTORY_PATH, [])


def log_event(now=None, **fields):
    """Add one event to the log and return it."""
    event = {"ts": (now or datetime.now()).isoformat(timespec="seconds"), **fields}
    history = load_history()
    history.append(event)
    write_json(paths.HISTORY_PATH, history)
    return event


def seen_counts(history):
    """How many times each question id has been asked."""
    counts = {}
    for event in history:
        if event.get("qid"):
            counts[event["qid"]] = counts.get(event["qid"], 0) + 1
    return counts
