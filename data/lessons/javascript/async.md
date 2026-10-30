# Async JavaScript (promises, async/await, the event loop)

JavaScript runs one thing at a time, but it can START slow work (network, timers) and come back when it finishes.

## Key ideas
- **Promise**: a value that will arrive later. States: pending, fulfilled, rejected.
- **then / catch**: `fetchUser().then(user => ...).catch(err => ...)`.
- **async / await**: `const user = await fetchUser();` pauses THIS function until the promise settles. `await` only works inside an `async` function (or at the top of a module).
- **Errors**: wrap awaits in `try { ... } catch (err) { ... }`.
- **In parallel**: `await Promise.all([a(), b(), c()])` starts all three together. Awaiting them one by one in a loop runs them in sequence (slower).
- **Event loop order**: synchronous code runs first, then promise callbacks (microtasks), then timers like `setTimeout` (macrotasks), even with a 0 ms delay.

## Example
```js
console.log("a");
setTimeout(() => console.log("b"), 0);
Promise.resolve().then(() => console.log("c"));
console.log("d");
// prints: a d c b
```

## Interview habit
When asked "what does this print?", walk through it in three buckets: sync first, then promises, then timers. For real code, mention error handling and whether independent calls should be parallel.
