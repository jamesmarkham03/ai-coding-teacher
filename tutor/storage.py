"""Small JSON read/write helpers shared by every module that keeps personal progress."""
import json
from pathlib import Path


def read_json(path, default):
    """Read a JSON file, or return `default` if it doesn't exist yet."""
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    """Write JSON via a temp file so a crash mid-write can't leave a half-written progress file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    temp.replace(path)
