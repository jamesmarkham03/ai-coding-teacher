# Arrays (JavaScript)

An **array** is an ordered list: `const nums = [4, 8, 15];`.

## Key ideas
- **Index and length**: `nums[0]`, `nums.length`. Use `nums.at(-1)` for the last item.
- **Change in place**: `push` (add to end, returns the new length), `pop`, `shift`, `unshift`, `splice`.
- **Make a new array** (original untouched): `map`, `filter`, `slice`, `concat`, spread `[...nums, 16]`.
- **Reduce to one value**: `nums.reduce((total, n) => total + n, 0)`.
- **Search**: `includes(x)`, `indexOf(x)`, `find(fn)`, `some(fn)`, `every(fn)`.
- **Loop**: `for (const n of nums)`; avoid `for...in` for arrays.
- **Sort gotcha**: `nums.sort()` sorts as TEXT. Use `nums.sort((a, b) => a - b)` for numbers.
- **Unique values**: `[...new Set(nums)]`.

## Example
```js
const nums = [1, 2, 3, 4];
const evens = nums.filter((n) => n % 2 === 0);   // [2, 4]
const doubled = nums.map((n) => n * 2);          // [2, 4, 6, 8]
const total = nums.reduce((a, b) => a + b, 0);   // 10
```

## Interview habit
Say whether your method changes the input. `sort`, `push` and `splice` mutate; `map`, `filter` and `slice` do not. Interviewers notice when you handle that on purpose.

In this tutor, write a plain function declaration (`function name(args) { ... }`) in the `.js` file. Tests run it with Node.
