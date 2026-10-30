# SELECT and filtering

SQL asks a database for rows from tables. The basic question has four parts: which columns, from which table, which rows, in what order.

## Key ideas
- **Shape**: `SELECT columns FROM table WHERE condition ORDER BY column LIMIT n;`
- **All columns**: `SELECT *` (fine to explore, avoid in real code).
- **Filter rows**: `WHERE age > 15 AND position <> 'P'`. Text uses single quotes. Combine with `AND`, `OR`, `NOT`, `IN (15, 16)`, `BETWEEN 10 AND 20`, `LIKE 'A%'`.
- **NULL is special**: use `IS NULL` / `IS NOT NULL`. `= NULL` never matches anything.
- **Sort**: `ORDER BY age DESC, name` (DESC = biggest first; default is ascending).
- **Unique values**: `SELECT DISTINCT position`.
- **First n rows**: `LIMIT 3`.
- **Rename a column**: `SELECT name AS player_name`.

## Example
```sql
SELECT name, age
FROM players
WHERE team = 'Comets' AND age >= 15
ORDER BY age DESC, name
LIMIT 5;
```

## Interview habit
Say the order the database really thinks in: FROM (which table), WHERE (which rows), then SELECT (which columns), then ORDER BY. It explains why you can't use a SELECT alias inside WHERE.

Tip for this tutor: write your query in the `.sql` file below the comment. A trailing `;` is fine.
