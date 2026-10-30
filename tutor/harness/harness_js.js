// Runs a student's JavaScript solution against test cases (same job as harness_python.py).
// Reads one JSON payload on stdin and prints one result line starting with the marker.
const fs = require("fs");
const vm = require("vm");

const MARKER = "@@RESULT@@";
const payload = JSON.parse(fs.readFileSync(0, "utf8"));

// Sets and Maps become plain arrays/objects so they can be compared as JSON.
function plain(value) {
  const json = JSON.stringify(value, (key, v) => {
    if (v instanceof Set) return [...v].sort();
    if (v instanceof Map) return Object.fromEntries(v);
    return v;
  });
  return json === undefined ? null : JSON.parse(json);
}

// Sort object keys (and list items when order doesn't matter) so equal data gives equal text.
function canon(value, unordered) {
  if (Array.isArray(value)) {
    const items = value.map((v) => canon(v, unordered));
    return unordered ? items.sort((a, b) => JSON.stringify(a).localeCompare(JSON.stringify(b))) : items;
  }
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map((k) => [k, canon(value[k], unordered)]));
  }
  return value;
}

function short(value) {
  const text = JSON.stringify(value);
  return text.length <= 200 ? text : text.slice(0, 200) + "...";
}

// unordered: false = exact, true = ignore order at every level, "outer" = only the top-level list.
function same(got, expected) {
  if (payload.unordered === "outer" && Array.isArray(got) && Array.isArray(expected)) {
    const key = (v) => JSON.stringify(canon(v, false));
    return JSON.stringify(got.map(key).sort()) === JSON.stringify(expected.map(key).sort());
  }
  return JSON.stringify(canon(got, !!payload.unordered)) === JSON.stringify(canon(expected, !!payload.unordered));
}

function finish(body) {
  console.log("\n" + MARKER + JSON.stringify(body));
}

const name = payload.function || payload.class;
const context = vm.createContext({ console });
let target;
try {
  // Re-export the name onto the context so `function` and `class` declarations are both reachable.
  vm.runInContext(payload.code + `\n;globalThis.__target = typeof ${name} === "undefined" ? undefined : ${name};`, context, { timeout: 4000 });
  target = context.__target;
  if (target === undefined) throw new Error(`your code must define \`${name}\``);
} catch (error) {
  finish({ load_error: String(error && error.message ? error.message : error) });
  process.exit(0);
}

const results = [];
for (const test of payload.tests) {
  try {
    let got;
    let label;
    if (payload.class) {
      label = `calls ${short(test.ops)}`;
      const instance = new target(...(test.init || []));
      got = test.ops.map((op) => plain(instance[op[0]](...op.slice(1))));
    } else {
      label = `input ${short(test.args)}`;
      got = plain(target(...JSON.parse(JSON.stringify(test.args))));
    }
    if (same(got, test.expected)) results.push({ ok: true });
    else results.push({ ok: false, msg: `${label}: expected ${short(test.expected)}, got ${short(got)}` });
  } catch (error) {
    results.push({ ok: false, msg: `input ${short(test.args || test.ops)}: ${error && error.name}: ${error && error.message}` });
  }
}
finish({ results });
