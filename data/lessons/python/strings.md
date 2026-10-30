# Strings

A **string** is text in quotes: `word = "Hello"`. Strings are **immutable**, so you cannot change one in place. Every operation returns a new string.

## Key ideas
- **Index and slice**: `word[0]` is `"H"`. `word[1:4]` is `"ell"` (the end is not included).
- **Length**: `len(word)` is `5`.
- **Methods**: `word.lower()`, `word.strip()`, `word.split(",")`, `", ".join(items)`, `word.startswith("He")`.
- **Check a character**: `ch.isalnum()` is True for letters and digits, which helps when you need to ignore punctuation.
- **Reverse**: `word[::-1]` gives the string backwards.
- **Build text**: collect pieces in a list, then `"".join(pieces)`. Adding strings in a loop is slow.

## Example
```python
s = "A man, a plan"
cleaned = [c.lower() for c in s if c.isalnum()]
print("".join(cleaned))        # amanaplan
print(cleaned == cleaned[::-1])  # False
```

## Interview habit
Clean the input first (lowercase, keep only letters and digits), then compare. Mention the two-pointer alternative: one pointer at each end moving inward checks the same thing without building a new string, using O(1) extra space.
