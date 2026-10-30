# Graphs

A **graph** is nodes connected by edges: cities and roads, people and friendships, courses and prerequisites.

## Key ideas
- **Adjacency list**: a dict from each node to the list of its neighbours: `{"a": ["b", "c"], "b": ["d"], "c": [], "d": []}`. This is the usual way to store a graph.
- **Directed vs undirected**: directed edges go one way (a -> b). For undirected, add the edge in both directions.
- **A grid is a graph**: each cell connects to its 4 neighbours (up, down, left, right).
- **visited set**: graphs can have cycles. Remember where you have been or you loop forever.
- **DFS** (stack or recursion): go as deep as possible, then back up. Good for "is there a path", "how many connected groups", cycle checks.
- **BFS** (queue): explore in rings of distance 1, 2, 3... Gives the shortest path when every edge counts the same.
- **Topological sort**: order items so each comes after its prerequisites. If you cannot order them all, there is a cycle.
- **Cost**: both searches are O(V + E): each node and each edge once.

## Example (BFS shortest path)
```python
from collections import deque
queue = deque([(start, 0)])
visited = {start}
while queue:
    node, dist = queue.popleft()
    if node == end:
        return dist
    for nxt in graph[node]:
        if nxt not in visited:
            visited.add(nxt)
            queue.append((nxt, dist + 1))
return -1
```

## Interview habit
First ask: what are the nodes, and what is an edge? Once you say "each cell is a node, neighbours are up/down/left/right", most grid problems become one of the patterns above.
