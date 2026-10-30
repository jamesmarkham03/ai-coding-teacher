# Heaps (priority queues)

A **heap** always gives you the smallest item quickly. It is the tool for "give me the best / smallest / largest next".

## Key ideas
- **Python's `heapq` is a min-heap.** `import heapq`.
- **Push and pop**: `heapq.heappush(h, x)` and `heapq.heappop(h)` are both O(log n). The smallest is always `h[0]` (peek is O(1)).
- **Build from a list**: `heapq.heapify(nums)` in O(n).
- **Max-heap trick**: push the negative of each number, negate again when you pop.
- **Tuples**: push `(priority, item)`. Python compares the first element, then the next on ties.
- **Helpers**: `heapq.nlargest(k, items)` and `heapq.nsmallest(k, items)`.
- **Top-k pattern**: to keep the k largest, hold a min-heap of size k and pop whenever it grows past k. The heap's top is then the k-th largest. Time O(n log k).

## Example
```python
import heapq
h = []
for n in [5, 1, 8, 3]:
    heapq.heappush(h, n)
print(heapq.heappop(h))  # 1
print(h[0])              # 3  (next smallest)
```

## Interview habit
If the problem says "k largest", "k most frequent", "closest k", or "merge k sorted", say "heap". Then state the size you will keep (usually k) because that is what makes it O(n log k) instead of O(n log n).
