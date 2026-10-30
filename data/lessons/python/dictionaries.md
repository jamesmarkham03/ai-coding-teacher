# Dictionaries

A **dictionary** (`dict`) stores key → value pairs: `ages = {"sam": 14, "lee": 15}`.

## Key ideas
- **Lookup**: `ages["sam"]` gives `14`. A missing key raises `KeyError`.
- **Safe lookup**: `ages.get("kim", 0)` returns `0` when the key is missing.
- **Set a value**: `ages["kim"] = 13` adds the key or updates it.
- **Keys must be hashable**: strings, numbers and tuples work. Lists do not.
- **Loop**: `for key, value in ages.items():` visits both at once.

## Interview habit
Counting things is the classic use. `counts[x] = counts.get(x, 0) + 1` counts any item in one line. Dictionaries give you O(1) average lookup, so they are often the answer when a problem says "find the pair" or "have I seen this before".
