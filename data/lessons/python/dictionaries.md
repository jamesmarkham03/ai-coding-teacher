# Dictionaries

A **dictionary** (`dict`) stores key -> value pairs: `ages = {"sam": 14, "lee": 15}`. Think of a roster: look up a name, get the age.

## Key ideas
- **Lookup**: `ages["sam"]` gives `14`. A missing key raises `KeyError`.
- **Safe lookup**: `ages.get("kim", 0)` returns `0` when the key is missing.
- **Set a value**: `ages["kim"] = 13` adds the key or updates it.
- **Keys must be hashable**: strings, numbers and tuples work. Lists do not.
- **Loop**: `for key, value in ages.items():` visits both at once.
- **Speed**: lookup, insert and delete are O(1) on average. That is why dicts solve so many problems.

## Example
```python
word = "banana"
counts = {}
for ch in word:
    counts[ch] = counts.get(ch, 0) + 1
print(counts)   # {'b': 1, 'a': 3, 'n': 2}
```

## Interview habit
Counting things is the classic use. Whenever a problem says "find the pair", "have I seen this before?" or "group by", reach for a dict. Store what you need to remember (a count, an index) as the value, so the second lookup is instant.
