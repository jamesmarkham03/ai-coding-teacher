# Functions, closures and classes (JavaScript)

## Functions
- **Declaration**: `function add(a, b) { return a + b; }`
- **Arrow function**: `const add = (a, b) => a + b;`
- **Default and rest**: `function f(a, b = 2, ...rest) {}`
- **First-class**: functions can be passed around, returned and stored: `nums.map((n) => n * 2)`.

## Closures
A function remembers the variables around it when it was created.
```js
const add = (a) => (b) => a + b;
const addFive = add(5);
console.log(addFive(3)); // 8
```
That is how counters, `once`, `memoize` and private state work.

## Equality
Use `===` (strict, no type conversion). `0 == "0"` is true; `0 === "0"` is false.

## Classes
```js
class Stack {
  constructor() { this.items = []; }
  push(x) { this.items.push(x); }
  pop() { return this.items.pop(); }
}
```
- `this` is the object the method was called on.
- Methods are written without the `function` keyword.
- `extends` and `super()` give inheritance.

## Interview habit
Be ready to explain a closure with a tiny counter example, and the difference between `let`, `const` and `var` (`var` is function-scoped and hoisted; prefer `const`).

In this tutor, class questions are tested by creating the class and calling its methods in order.
