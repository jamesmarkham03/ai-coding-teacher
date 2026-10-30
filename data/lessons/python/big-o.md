# Big-O (how fast, how much memory)

**Big-O** describes how the work grows when the input grows. It ignores small details and answers: "if the input doubles, what happens to the time?"

## The usual suspects (fast to slow)
| Name | Looks like | Example |
|------|-----------|---------|
| O(1) constant | same time always | dict lookup, list index |
| O(log n) | halves the problem each step | binary search |
| O(n) linear | one pass | loop through a list once |
| O(n log n) | sort-like | `sorted()`, merge sort |
| O(n^2) quadratic | loop inside a loop | compare every pair |
| O(2^n) exponential | tries every subset | naive recursion on subsets |

## How to work it out
- Count the loops. Nested loops over the input multiply: n * n.
- Sequential loops add, and you keep only the biggest term: O(n + n) is O(n).
- Drop constants: O(3n) is O(n).
- **Space** counts the extra memory you use (not the input). A new list of size n is O(n) space.

## Cheat sheet for Python
- `x in list` is O(n). `x in set` and `x in dict` are O(1) average.
- `list.append`, `list.pop()` are O(1). `list.insert(0, x)` and `list.pop(0)` are O(n). Use `deque` for queues.
- `sorted(...)` is O(n log n).
- Slicing `nums[a:b]` copies, so it costs O(b - a).

## Interview habit
After you code a solution, say its time and space complexity without being asked, and name one trade-off ("I could save memory with two pointers, but I'd have to sort first, which costs O(n log n)").
