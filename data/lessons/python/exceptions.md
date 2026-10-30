# Exceptions

An **exception** is Python's way of saying "something went wrong here". If nothing handles it, the program stops.

## Key ideas
- **try / except**: run risky code, handle the failure.
- **Catch specific errors**: `except ValueError:` not a bare `except:`. A broad catch hides real bugs.
- **else**: runs only if no exception happened. **finally**: runs no matter what (good for cleanup).
- **raise**: signal a problem yourself: `raise ValueError("age must be positive")`.
- **Common ones**: `ValueError` (bad value), `TypeError` (wrong type), `KeyError` (missing dict key), `IndexError` (list index out of range), `ZeroDivisionError`.
- **Ask forgiveness vs permission**: Python code often just tries it and handles the error, instead of checking first.

## Example
```python
def parse_int(text, default):
    try:
        return int(text)
    except ValueError:
        return default

print(parse_int("42", 0))   # 42
print(parse_int("abc", 0))  # 0
```

## Interview habit
State your edge-case choices: "If the input is empty I'll return an empty list rather than raise." Interviewers like to hear that you thought about bad input, and a short `try/except` is a clean way to handle it.
