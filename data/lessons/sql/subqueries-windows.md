# Subqueries and window functions

## Subqueries
A **subquery** is a query inside a query.
- **In WHERE**: `WHERE hits > (SELECT AVG(hits) FROM stats)` compares each row with one calculated value.
- **In FROM**: treat a query result as a temporary table: `FROM (SELECT ... ) AS t`.
- **CTE**: `WITH totals AS (SELECT ...) SELECT ... FROM totals;` is a readable way to name a step.
- **IN / EXISTS**: `WHERE id IN (SELECT player_id FROM ...)`.

## Window functions
A **window function** calculates across related rows but keeps every row (GROUP BY collapses them).
- Shape: `function() OVER (PARTITION BY group ORDER BY order)`.
- **Running total**: `SUM(hits) OVER (PARTITION BY player ORDER BY game)`.
- **Ranking**: `RANK()` (ties share a rank, then a gap: 1,1,3), `DENSE_RANK()` (1,1,2), `ROW_NUMBER()` (always unique).
- **Previous / next row**: `LAG(hits) OVER (...)`, `LEAD(hits) OVER (...)`.
- Top n per group: rank inside a subquery or CTE, then filter `WHERE rnk <= n`.

## Example
```sql
SELECT player, game,
       SUM(hits) OVER (PARTITION BY player ORDER BY game) AS running_hits
FROM stats;
```

## Interview habit
"Highest per group" and "running total" are the two classics. Say "that's a window function" and name PARTITION BY (the group) and ORDER BY (the order within it).
