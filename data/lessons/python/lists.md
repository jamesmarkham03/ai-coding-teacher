# Lists

A **list** is an ordered collection of items, written with square brackets: `nums = [4, 8, 15]`. It is the workhorse of Python and of most interview answers.

## Key ideas
- **Index**: each item has a position, starting at `0`. `nums[0]` is `4`.
- **Negative index**: counts from the end. `nums[-1]` is the last item.
- **Slice**: `nums[1:3]` gives the items at positions 1 and 2. The end is not included. `nums[:]` is a copy.
- **Mutable**: you can change a list in place with `append`, `pop`, `insert` or `nums[0] = 10`.
- **Loop**: `for n in nums:` visits each item. `for i, n in enumerate(nums):` gives the position too.
- **Cost**: reading by index and `append` are fast (O(1)). `x in nums` and `insert(0, x)` have to walk the list (O(n)).

## Example
```python
nums = [4, 8, 15, 16]
print(nums[-1])      # 16
print(nums[1:3])     # [8, 15]
nums.append(23)      # [4, 8, 15, 16, 23]
copy = nums[:]       # a separate list with the same items
```

## Interview habit
When a problem asks for a new list, build a new list and leave the input alone. If you need to ask "have I seen this value?", use a `set` instead of scanning the list again. That one swap turns many O(n^2) answers into O(n).
