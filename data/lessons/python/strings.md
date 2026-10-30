# Strings

A **string** is text in quotes: `word = "Hello"`. Strings are **immutable**, so you cannot change one in place. Every operation returns a new string.

## Key ideas
- **Index and slice**: `word[0]` is `"H"`. `word[1:4]` is `"ell"` (the end is not included).
- **Length**: `len(word)` is `5`.
- **Methods**: `word.lower()`, `word.strip()`, `word.split(",")`, `", ".join(items)`.
- **Check a character**: `ch.isalnum()` is True for letters and digits, which helps when you need to ignore punctuation.
- **Reverse**: `word[::-1]` gives the string backwards.

## Interview habit
Clean the input first (lowercase, keep only letters and digits), then compare it with its reverse. Two pointers, one at each end moving inward, check the same thing without building a new string.
