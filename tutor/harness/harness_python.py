"""Runs a student's Python solution against test cases.

Reads one JSON payload on stdin and prints one result line starting with the marker.
This runs in its own process so an infinite loop or crash in student code cannot take the tutor down.

Payload: {"code", "function" | "class", "tests", "unordered", "returns"}
"""
import json
import sys

MARKER = "@@RESULT@@"


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def build_tree(values):
    """Build a binary tree from a level-order list where None means 'no node' (LeetCode style)."""
    if not values:
        return None
    nodes = [None if v is None else TreeNode(v) for v in values]
    children = iter(nodes[1:])
    for node in nodes:
        if node is None:
            continue
        try:
            node.left = next(children)
            node.right = next(children)
        except StopIteration:
            break
    return nodes[0]


def tree_to_list(root):
    out, queue = [], [root]
    while queue:
        node = queue.pop(0)
        if node is None:
            out.append(None)
        else:
            out.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


def build_list(values):
    head = None
    for value in reversed(values):
        head = ListNode(value, head)
    return head


def list_to_list(head):
    out = []
    while head is not None and len(out) < 10000:  # cap guards against a cycle in broken code
        out.append(head.val)
        head = head.next
    return out


def convert_arg(arg):
    if isinstance(arg, dict):
        if "$tree" in arg:
            return build_tree(arg["$tree"])
        if "$list" in arg:
            return build_list(arg["$list"])
    return arg


def _default(obj):
    if isinstance(obj, (set, frozenset)):
        return sorted(obj)
    raise TypeError(f"can't compare a value of type {type(obj).__name__}")


def plain(value):
    """Turn a return value into plain JSON data (tuples become lists, sets become sorted lists)."""
    return json.loads(json.dumps(value, default=_default))


def canon(value):
    """Sort lists recursively so answers whose order doesn't matter can be compared."""
    if isinstance(value, list):
        return sorted((canon(v) for v in value), key=lambda v: json.dumps(v, sort_keys=True))
    if isinstance(value, dict):
        return {k: canon(v) for k, v in value.items()}
    return value


def short(value, limit=200):
    text = repr(value)
    return text if len(text) <= limit else text[:limit] + "..."


def matches(got, expected, unordered):
    """unordered: False = exact, True = ignore order at every level, "outer" = only the top list."""
    if unordered == "outer" and isinstance(got, list):
        key = lambda v: json.dumps(v, sort_keys=True)
        return sorted(got, key=key) == sorted(expected, key=key)
    if unordered:
        return canon(got) == canon(expected)
    return got == expected


def run_function_tests(payload, target):
    results = []
    for test in payload["tests"]:
        label = f"input {short(test['args'])}"
        try:
            got = target(*[convert_arg(a) for a in test["args"]])
            if payload.get("returns") == "tree":
                got = tree_to_list(got)
            elif payload.get("returns") == "list":
                got = list_to_list(got)
            got = plain(got)
        except Exception as error:  # student code can raise anything
            results.append({"ok": False, "msg": f"{label}: {type(error).__name__}: {error}"})
            continue
        if matches(got, test["expected"], payload.get("unordered")):
            results.append({"ok": True})
        else:
            results.append({"ok": False, "msg": f"{label}: expected {short(test['expected'])}, got {short(got)}"})
    return results


def run_class_tests(payload, cls):
    results = []
    for test in payload["tests"]:
        label = f"calls {short(test['ops'])}"
        try:
            instance = cls(*test.get("init", []))
            got = [plain(getattr(instance, op[0])(*op[1:])) for op in test["ops"]]
        except Exception as error:
            results.append({"ok": False, "msg": f"{label}: {type(error).__name__}: {error}"})
            continue
        if got == test["expected"]:
            results.append({"ok": True})
        else:
            results.append({"ok": False, "msg": f"{label}: expected {short(test['expected'])}, got {short(got)}"})
    return results


def main():
    payload = json.load(sys.stdin)
    namespace = {"TreeNode": TreeNode, "ListNode": ListNode, "__name__": "solution"}
    name = payload.get("function") or payload.get("class")
    try:
        exec(compile(payload["code"], "solution", "exec"), namespace)
        if name not in namespace:
            raise NameError(f"your code must define `{name}`")
    except BaseException as error:
        print("\n" + MARKER + json.dumps({"load_error": f"{type(error).__name__}: {error}"}))
        return

    runner = run_class_tests if payload.get("class") else run_function_tests
    results = runner(payload, namespace[name])
    print("\n" + MARKER + json.dumps({"results": results}))


if __name__ == "__main__":
    main()
