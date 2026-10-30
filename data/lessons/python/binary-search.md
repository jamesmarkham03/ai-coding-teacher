# Binary search

Find something in **sorted** data by cutting the search range in half every step. 1,000,000 items take about 20 steps.

## Key ideas
- **Setup**: `lo = 0`, `hi = len(nums) - 1`.
- **Loop**: `while lo <= hi:` look at `mid = (lo + hi) // 2`.
  - found it: return `mid`
  - `nums[mid] < target`: the answer is to the right, so `lo = mid + 1`
  - otherwise: the answer is to the left, so `hi = mid - 1`
- **Off-by-one care**: always move PAST mid (`mid + 1` / `mid - 1`), or the loop can get stuck forever.
- **When the loop ends**, `lo` is the position where the target would be inserted.
- **Binary search on the answer**: you can also search a range of possible answers (speeds, capacities) if "does this answer work?" flips from false to true exactly once. Search for the smallest value that works.
- **Built in**: `bisect.bisect_left(nums, x)` does it for you. Know how to write it by hand first.
- **Cost**: O(log n) time, O(1) space.

## Example
```python
lo, hi = 0, len(nums) - 1
while lo <= hi:
    mid = (lo + hi) // 2
    if nums[mid] == target:
        return mid
    if nums[mid] < target:
        lo = mid + 1
    else:
        hi = mid - 1
return -1
```

## Interview habit
Test your loop on 3 cases out loud: one item, two items, and a target that is missing at either end. Those catch nearly every off-by-one bug.
