"""Checks a student's solution against a question's test cases, for every supported language.

Python and JavaScript run in a separate process with a timeout. SQL runs on an in-memory
SQLite database. Every runner returns the same Result so the session code stays simple.
"""
import json
import sqlite3
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent / "harness"
MARKER = "@@RESULT@@"
EXTENSIONS = {"python": ".py", "sql": ".sql", "javascript": ".js"}
DEFAULT_TIMEOUT = 5  # seconds; matches the "your code is too slow" feeling of a real interview


@dataclass
class Result:
    passed: bool
    n_passed: int = 0
    n_total: int = 0
    failures: list = field(default_factory=list)
    error: str = ""  # the code could not run at all (syntax error, missing function, timeout)
    output: str = ""  # what the student's code printed


def extension_for(language):
    return EXTENSIONS[language]


def starter_code(question):
    """The file a student starts from: the prompt as a comment plus an empty function to fill in."""
    language = question["language"]
    prompt_lines = question["prompt"].splitlines()
    if question.get("starter"):
        body = question["starter"]
    elif language == "python":
        body = f"def {question['function']}({question.get('params', '')}):\n    pass\n"
    elif language == "javascript":
        body = f"function {question['function']}({question.get('params', '')}) {{\n\n}}\n"
    else:
        body = "SELECT \n"
    comment = "--" if language == "sql" else "//" if language == "javascript" else "#"
    header = "\n".join(f"{comment} {line}" for line in prompt_lines)
    return f"{header}\n\n{body}"


def check_solution(question, code, timeout=DEFAULT_TIMEOUT):
    """Run `code` against the question's tests and return a Result."""
    language = question["language"]
    if language == "sql":
        return _run_sql(question, code, timeout)
    return _run_subprocess(question, code, timeout)


def _run_subprocess(question, code, timeout):
    language = question["language"]
    payload = {
        "code": code,
        "function": question.get("function"),
        "class": question.get("class"),
        "tests": question["tests"],
        "unordered": question.get("unordered", False),
        "returns": question.get("returns"),
    }
    if language == "python":
        command = [sys.executable, "-I", str(HARNESS_DIR / "harness_python.py")]
    else:
        command = ["node", str(HARNESS_DIR / "harness_js.js")]

    try:
        done = subprocess.run(command, input=json.dumps(payload), capture_output=True, text=True,
                              encoding="utf-8", timeout=timeout)
    except FileNotFoundError:
        return Result(False, error="Node.js is not installed, so JavaScript can't run.")
    except subprocess.TimeoutExpired:
        return Result(False, error=f"Timed out after {timeout}s. Check for an infinite loop or a slow approach.")

    lines = done.stdout.splitlines()
    marker_lines = [line for line in lines if line.startswith(MARKER)]
    printed = "\n".join(line for line in lines if not line.startswith(MARKER)).strip()[:500]
    if not marker_lines:
        crash = (done.stderr or "no output").strip().splitlines()
        return Result(False, error=crash[-1] if crash else "the program crashed", output=printed)

    body = json.loads(marker_lines[-1][len(MARKER):])
    if "load_error" in body:
        return Result(False, error=body["load_error"], output=printed)
    results = body["results"]
    failures = [r["msg"] for r in results if not r["ok"]]
    return Result(not failures, len(results) - len(failures), len(results), failures, output=printed)


def _normalize_rows(rows, ordered):
    cleaned = [[round(v, 2) if isinstance(v, float) else v for v in row] for row in rows]
    return cleaned if ordered else sorted(cleaned, key=lambda r: json.dumps(r))


def _run_sql(question, code, timeout):
    connection = sqlite3.connect(":memory:")
    started = time.time()
    # Abort a runaway query (sqlite calls this every 10,000 steps).
    connection.set_progress_handler(lambda: 1 if time.time() - started > timeout else 0, 10000)
    try:
        connection.executescript(question["setup"])
        query = "\n".join(l for l in code.splitlines() if not l.strip().startswith("--"))
        query = query.strip().rstrip(";").strip()
        if query.upper() in ("", "SELECT"):
            return Result(False, error="Write your query below the comment first.")
        got = [list(row) for row in connection.execute(query).fetchall()]
    except sqlite3.Error as error:
        return Result(False, error=f"SQL error: {error}")
    finally:
        connection.close()

    ordered = question.get("ordered", False)
    got_rows = _normalize_rows(got, ordered)
    expected_rows = _normalize_rows(question["expected"], ordered)
    if got_rows == expected_rows:
        return Result(True, 1, 1)
    message = f"expected {len(expected_rows)} rows {expected_rows[:5]}, got {len(got_rows)} rows {got_rows[:5]}"
    if not ordered:
        message += " (row order doesn't matter here)"
    return Result(False, 0, 1, [message])
