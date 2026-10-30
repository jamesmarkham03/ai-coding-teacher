# Objects and Maps (JavaScript)

An **object** stores key -> value pairs: `const ages = { sam: 14, lee: 15 };`. It plays the role of Python's dict.

## Key ideas
- **Read / write**: `ages.sam`, `ages["sam"]`, `ages.kim = 13`. A missing key gives `undefined`.
- **Check a key**: `"sam" in ages` or `ages.hasOwnProperty("sam")`.
- **Loop**: `Object.keys(ages)`, `Object.values(ages)`, `Object.entries(ages)`.
- **Copy / merge**: `{ ...a, ...b }`.
- **Counting pattern**: `counts[w] = (counts[w] || 0) + 1`. And `(groups[k] ||= []).push(item)` to group.
- **Map**: `new Map()` with `set`, `get`, `has`. Keys can be any type, and it keeps insertion order. Good for lookup tables like two-sum.
- **Set**: `new Set()` for unique values.
- **Gotchas**: `typeof null` is `"object"`. Object keys become strings. `{} === {}` is false (objects compare by reference).

## Example
```js
const counts = {};
for (const ch of "banana") {
  counts[ch] = (counts[ch] || 0) + 1;
}
console.log(counts);   // { b: 1, a: 3, n: 2 }
```

## Interview habit
Same story as Python: lookups in an object, Map or Set are O(1) on average. Reach for them whenever you would otherwise scan an array again.
