# Sets

A **set** is an unordered collection of unique values: `seen = {1, 2, 3}`. Adding something already there does nothing.

## Key ideas
- **Create**: `set([1, 2, 2, 3])` gives `{1, 2, 3}`. An empty set is `set()`, not `{}` (that is an empty dict).
- **Membership**: `x in seen` is O(1) on average. In a list it would be O(n).
- **Add / remove**: `seen.add(4)`, `seen.discard(4)`.
- **Set math**: `a & b` (in both), `a | b` (in either), `a - b` (in a but not b).
- **No order, no index**: you cannot write `seen[0]`. Wrap in `sorted(seen)` when you need order.

## Example
```python
a = [1, 2, 2, 3]
b = [2, 3, 4]
print(len(set(a)) != len(a))   # True (a has a duplicate)
print(sorted(set(a) & set(b))) # [2, 3]
```

## Interview habit
"Have I seen this value before?" is a set question. Say it out loud: "I'll keep a set of values I've seen so each check is O(1)." It is the quickest way to show you understand the cost of a lookup.
