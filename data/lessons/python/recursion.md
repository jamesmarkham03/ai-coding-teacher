# Recursion

A function is **recursive** when it calls itself on a smaller version of the problem.

## Key ideas
- **Base case**: the smallest problem you can answer directly (`n <= 1`, empty list, `None` node). Without it, the calls never stop.
- **Recursive case**: shrink the problem and trust the call to solve the smaller one.
- **Call stack**: every call waits in memory. Python allows about 1000 nested calls, then raises `RecursionError`.
- **Choose / don't choose**: for subsets, permutations and brackets, you decide at each step, recurse, then undo (backtracking).
- **Watch for repeats**: naive Fibonacci recomputes the same values and is O(2^n). Caching answers (memoization, see dynamic programming) fixes that.

## Example
```python
def power_set(nums):
    if not nums:
        return [[]]                       # base case: one subset, the empty one
    rest = power_set(nums[1:])            # trust it solves the smaller problem
    return rest + [[nums[0]] + s for s in rest]
```

## How to think about it
1. What is the smallest case and its answer?
2. If I already had the answer for a slightly smaller input, how would I build mine?
3. Does each call move toward the base case?

## Interview habit
Say the three questions above out loud. Also mention the stack depth: "recursion uses O(n) stack space; I could do this iteratively if the input might be very deep."
