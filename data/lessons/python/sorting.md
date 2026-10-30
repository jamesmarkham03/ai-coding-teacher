# Sorting

Putting items in order is often step one of a harder problem.

## Key ideas
- **`sorted(items)`** returns a NEW sorted list. **`items.sort()`** sorts in place and returns `None`.
- **`reverse=True`** sorts largest first.
- **`key=`** says what to compare: `sorted(words, key=len)`, `sorted(people, key=lambda p: p["age"])`. Sort by several things with a tuple: `key=lambda p: (p["team"], -p["age"])`.
- **Stable**: items that compare equal keep their original order.
- **Cost**: built-in sort is O(n log n). Any comparison sort needs at least that.
- **Merge sort idea**: split in half, sort each half, merge the two sorted halves with two pointers. O(n log n) time, O(n) extra space.
- **Why sort first?** Sorted data lets you use two pointers or binary search, group equal items next to each other, and merge overlapping ranges.

## Example
```python
intervals = [[8, 10], [1, 3], [2, 6]]
intervals.sort()               # [[1, 3], [2, 6], [8, 10]]
words = ["bb", "a", "ccc"]
print(sorted(words, key=len))  # ['a', 'bb', 'ccc']
```

## Interview habit
When a problem feels messy, ask "would this be easier if the input were sorted?" Spending O(n log n) on a sort to get an O(n) pass is often a good deal. Say the total cost out loud.
