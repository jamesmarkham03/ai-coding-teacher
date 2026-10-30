# Classes

A **class** is a blueprint for objects that bundle data (attributes) with the actions that use it (methods). A `BankAccount` object holds a balance and knows how to deposit.

## Key ideas
- **Define**: `class Counter:` and create objects with `c = Counter()`.
- **`__init__`**: runs when the object is created. It sets up the starting data.
- **`self`**: the specific object a method was called on. Every method takes it first.
- **Attributes**: data stored on the object, `self.count = 0`.
- **Methods**: functions inside the class, `def increment(self): self.count += 1`.
- **Convention**: a leading underscore (`self._balance`) means "internal, please don't touch from outside".
- **Inheritance**: `class Savings(BankAccount):` reuses and extends a parent class.
- **`__str__`**: controls what `print(obj)` shows.

## Example
```python
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1

c = Counter()
c.increment()
c.increment()
print(c.count)  # 2
```

## Interview habit
Design questions ("design a cache", "design a parking lot") are about picking the right data and the right methods. Say the interface first (what methods, what they return), then pick the data structure behind it, then code it.
