# Lists

A **list** is an ordered collection of items, written with square brackets: `nums = [4, 8, 15]`.

## Key ideas
- **Index**: each item has a position, starting at `0`. `nums[0]` is `4`.
- **Negative index**: counts from the end. `nums[-1]` is the last item.
- **Slice**: `nums[1:3]` gives items at positions 1 and 2 (the end is not included).
- **Mutable**: you can change a list in place with `append`, `pop`, or `nums[0] = 10`.
- **Loop**: `for n in nums:` visits each item in order.

## Interview habit
When a problem asks for a new list, build a new list and leave the input alone. If you need to know whether you have already seen a value, a `set` lookup is much faster than scanning the list again.
