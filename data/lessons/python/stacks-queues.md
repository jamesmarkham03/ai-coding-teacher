# Stacks and queues

Both hold items in order. They differ in which end you take from.

- **Stack**: last in, first out (LIFO). Like a pile of plates.
- **Queue**: first in, first out (FIFO). Like a line at a checkout.

## Key ideas
- **Stack in Python**: a plain list. `stack.append(x)` to push, `stack.pop()` to pop, `stack[-1]` to peek. All O(1).
- **Queue in Python**: `from collections import deque`. `q.append(x)` to add, `q.popleft()` to remove from the front. Both O(1). (`list.pop(0)` is O(n), so don't use a list for a queue.)
- **Use a stack when** you need to undo, match pairs (brackets), or remember "what came before that is still unresolved".
- **Use a queue when** you process things in the order they arrived: breadth-first search, task scheduling.
- **Monotonic stack**: a stack that stays sorted. It answers "next greater element" questions in O(n).

## Example
```python
stack = []
for ch in "(a)":
    if ch == "(":
        stack.append(ch)
    elif ch == ")":
        stack.pop()
print(len(stack) == 0)   # True: brackets matched
```

## Interview habit
"Pairs that must match in order" almost always means stack. Say it: "Each closing bracket must match the most recent unmatched opener, so I'll use a stack."
