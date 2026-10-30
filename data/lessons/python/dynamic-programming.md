# Dynamic programming (DP)

DP solves a big problem by solving smaller overlapping problems once and reusing the answers. It is "recursion that remembers".

## Key ideas
- **Overlapping subproblems**: the same smaller question comes up again and again (fib(3) is needed by both fib(5) and fib(4)).
- **Optimal substructure**: the best answer is built from best answers of smaller pieces.
- **Top-down (memoization)**: write the recursion, then cache results: `@functools.cache` above the function.
- **Bottom-up (table)**: fill an array from the smallest case upward. Often lets you keep only the last one or two values (O(1) space).
- **How to start**:
  1. Define the state: "`best[i]` = the answer for the first i items" (or for amount i, or for the cell at i, j).
  2. Write the rule that builds `best[i]` from earlier entries.
  3. Set the starting values.
  4. Decide the order to fill and where the final answer sits.

## Example (climbing stairs)
```python
def climb_stairs(n):
    a, b = 1, 1                 # ways to reach step 0 and step 1
    for _ in range(n - 1):
        a, b = b, a + b         # ways(i) = ways(i-1) + ways(i-2)
    return b
```

## Interview habit
Start with the plain recursive idea even if it is slow, say why it repeats work, then add the cache. That path (brute force -> spot repeats -> memoize -> maybe a table) is exactly the story interviewers want to hear.
