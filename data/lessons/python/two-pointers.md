# Two pointers

Use two index variables that move through the data, instead of a nested loop. It turns many O(n^2) answers into O(n).

## Two flavours
1. **Opposite ends**: `left = 0`, `right = len - 1`, move them toward each other. Great for sorted arrays, palindromes, reversing, and "container" problems.
2. **Same direction (fast and slow)**: both start at the left. One scans ahead while the other marks where to write or the start of a range. Great for removing duplicates and linked-list tricks.

## Key ideas
- **Sorted pair sum**: if `nums[left] + nums[right]` is too small, move `left` right (bigger). If too big, move `right` left (smaller). Each step rules out a whole group of pairs.
- **Stop condition**: usually `while left < right`.
- **Skip duplicates** when the answer must be unique (three-sum).
- **Cost**: one pass, O(n), and O(1) extra space.

## Example
```python
left, right = 0, len(nums) - 1
while left < right:
    total = nums[left] + nums[right]
    if total == target:
        return [left, right]
    if total < target:
        left += 1
    else:
        right -= 1
```

## Interview habit
Before coding, explain WHY moving a pointer is safe ("moving the taller line can never improve the area, so I always move the shorter one"). That reasoning is what the interviewer is listening for.
