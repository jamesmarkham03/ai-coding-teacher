# Sliding window

A **window** is a stretch of consecutive items, tracked by a left and right edge. Instead of recomputing each window from scratch, you slide it and update the answer.

## Two kinds
1. **Fixed size k**: add the new item on the right, drop the old item on the left. "Largest sum of k in a row."
2. **Variable size**: grow the right edge each step. When the window breaks a rule, shrink from the left until it is valid again. "Longest stretch with no repeated letter", "shortest run with sum at least X."

## Key ideas
- Keep a running value (a sum, a set, a dict of counts) that describes the current window.
- Each item enters once and leaves once, so the total work is O(n).
- Typical shape for a variable window:

```python
left = 0
for right, item in enumerate(items):
    # add items[right] to the window
    while window_is_invalid:
        # remove items[left] from the window
        left += 1
    # window is valid here; update the best answer
```

## Example
```python
window = sum(nums[:k])
best = window
for i in range(k, len(nums)):
    window += nums[i] - nums[i - k]   # slide by one
    best = max(best, window)
```

## Interview habit
Clue words: "contiguous", "substring", "subarray", "consecutive". When you hear them, say "sliding window" and say what you will track inside it.
