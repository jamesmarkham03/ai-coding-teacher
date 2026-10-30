# Functions

A **function** is a named, reusable block of code. It takes inputs (parameters) and hands back an output (`return`).

## Key ideas
- **Define and call**: `def add(a, b): return a + b`, then `add(2, 3)`.
- **No return** means the function gives back `None`.
- **Default values**: `def greet(name, greeting="Hello"):` so `greet("Sam")` works.
- **Any number of arguments**: `def total(*nums):` collects extras into a tuple.
- **Keyword arguments**: `greet(name="Sam", greeting="Hi")`, order doesn't matter.
- **Scope**: variables created inside a function exist only inside it.
- **Lambda**: a one-line anonymous function, handy as `key=lambda x: x[1]`.
- **Trap**: never use a mutable default like `items=[]`. It is created once and shared by every call. Use `items=None` and make the list inside.

## Example
```python
def make_greeting(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(make_greeting("Sam"))        # Hello, Sam!
print(make_greeting("Sam", "Hi"))  # Hi, Sam!
```

## Interview habit
Small functions with clear names are easier to test and to explain. When you describe a solution, name the helper you would write ("I'd write `is_valid(row, col)` for the bounds check") before you write its body.
