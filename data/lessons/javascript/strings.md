# Strings (JavaScript)

A **string** is immutable text: `const word = "Hello";`.

## Key ideas
- **Access**: `word[0]`, `word.length`, `word.at(-1)`.
- **Slice**: `word.slice(1, 3)` is `"el"` (end not included).
- **Case and trim**: `toLowerCase()`, `toUpperCase()`, `trim()`.
- **Split and join**: `"a b".split(" ")` gives `["a", "b"]`; `["a", "b"].join("-")` gives `"a-b"`.
- **Search**: `includes`, `startsWith`, `indexOf`.
- **Replace with a pattern**: `s.replace(/[^a-z0-9]/g, "")` removes everything except letters and digits (the `g` flag means all matches).
- **Reverse**: `[...s].reverse().join("")`. Strings have no reverse method.
- **Template strings**: `` `Hello, ${name}!` ``.
- **Type gotcha**: `"5" + 3` is `"53"` (text), but `"5" - 3` is `2` (number).

## Example
```js
const s = "A man, a plan";
const cleaned = s.toLowerCase().replace(/[^a-z0-9]/g, "");
console.log(cleaned);                                     // amanaplan
console.log(cleaned === [...cleaned].reverse().join("")); // false
```

## Interview habit
Strings are immutable, so building one with `+=` in a big loop is wasteful. Collect pieces in an array and `join` at the end.
