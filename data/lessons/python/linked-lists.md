# Linked lists

A **linked list** is a chain of nodes. Each node holds a value and a pointer to the next node. The list is just a reference to the first node, the **head**.

```
head -> [1] -> [2] -> [3] -> None
```

## Key ideas
- **Node**: `ListNode(val, next)`. `node.val` is the value, `node.next` is the next node (or `None` at the end).
- **Walk the list**: `while node: ...; node = node.next`.
- **Cost**: reaching the k-th node takes O(k) because you must follow the links. Inserting or removing after a node you already have is O(1) (just rewire pointers).
- **Dummy node**: start with a fake node before the head (`dummy = ListNode(0, head)`). It removes special cases when the head changes. Return `dummy.next`.
- **Fast and slow pointers**: slow moves 1 step, fast moves 2. When fast reaches the end, slow is in the middle. If fast ever meets slow, the list has a cycle.
- **Reversing**: keep `prev`, `node`, and save `node.next` before you overwrite it.

## Example
```python
prev, node = None, head
while node:
    nxt = node.next      # save it first!
    node.next = prev     # flip the arrow
    prev, node = node, nxt
return prev              # new head
```

## Interview habit
Draw the boxes and arrows before coding, and watch for the two classic bugs: losing the rest of the list because you overwrote `next` too early, and forgetting the empty list or one-node list.

In this tutor, `ListNode` is already defined for you, and tests give you lists like `[1, 2, 3]` converted into nodes.
