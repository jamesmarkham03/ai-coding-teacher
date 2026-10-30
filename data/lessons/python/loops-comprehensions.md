# Loops and comprehensions

A **loop** repeats work. A **comprehension** is a compact way to build a list from a loop.

## Key ideas
- **for loop**: `for x in items:` visits each item. `for i in range(5):` counts 0 to 4.
- **enumerate**: `for i, x in enumerate(items):` gives the position and the item.
- **zip**: `for a, b in zip(list1, list2):` walks two lists side by side.
- **while loop**: `while condition:` repeats until the condition is false. Make sure something inside changes it, or it never ends.
- **break / continue**: stop the loop, or skip to the next item.
- **List comprehension**: `[x * x for x in nums if x % 2 == 0]` means "square each even number". The shape is `[expression for item in items if condition]`.
- Dict and set versions exist too: `{w: len(w) for w in words}`.

## Example
```python
nums = [1, 2, 3, 4]
squares = [n * n for n in nums]            # [1, 4, 9, 16]
evens = [n for n in nums if n % 2 == 0]    # [2, 4]
pairs = [(i, n) for i, n in enumerate(nums)]
```

## Interview habit
A comprehension is fine when it fits on one readable line. If you need nested conditions, write the plain loop. Interviewers prefer clear over clever.
