# Trees

A **binary tree** is made of nodes, each with a value and up to two children: `left` and `right`. The top node is the **root**. A node with no children is a **leaf**.

```
      3
     / \
    9   20
       /  \
      15   7
```

## Key ideas
- **Node**: `TreeNode(val, left, right)`. A missing child is `None`.
- **Depth-first search (DFS)**: go deep first, usually with recursion. Three orders: pre-order (node, left, right), in-order (left, node, right), post-order (left, right, node).
- **Breadth-first search (BFS)**: level by level, using a queue (`deque`).
- **The recursion pattern**: handle `None` first (the base case), then combine the answers from `node.left` and `node.right`.
- **Binary search tree (BST)**: everything in the left subtree is smaller, everything in the right is larger. In-order traversal gives sorted output.
- **Height**: a balanced tree with n nodes is about log2(n) tall. A lopsided one can be n tall.

## Example
```python
def max_depth(node):
    if node is None:
        return 0
    return 1 + max(max_depth(node.left), max_depth(node.right))
```

## Interview habit
Most tree problems are the same three lines: if the node is None return the empty answer, recurse left and right, combine. Say what each recursive call RETURNS before writing it. In this tutor `TreeNode` is already defined, and tests pass trees as level-order lists like `[3, 9, 20, null, null, 15, 7]`.
