# Aggregation and GROUP BY

**Aggregate functions** turn many rows into one value: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`.

## Key ideas
- **Whole table**: `SELECT COUNT(*) FROM stats;` gives one row.
- **GROUP BY**: one result row per group: `SELECT player, SUM(hits) FROM stats GROUP BY player;`
- **Rule**: every column in SELECT must either be in GROUP BY or inside an aggregate.
- **WHERE vs HAVING**: WHERE filters rows BEFORE grouping. HAVING filters groups AFTER: `HAVING SUM(hits) > 3`.
- **COUNT(*) vs COUNT(col)**: `COUNT(*)` counts all rows. `COUNT(col)` skips NULLs. `COUNT(DISTINCT col)` counts unique values.
- **Division**: whole-number division truncates. Use `1.0 * a / b` to get decimals, and `ROUND(x, 3)` to tidy up.

## Example (a batting average)
```sql
SELECT player,
       ROUND(1.0 * SUM(hits) / SUM(at_bats), 3) AS avg
FROM stats
GROUP BY player
ORDER BY avg DESC;
```
Note: an average of per-game averages is wrong. Add up hits and at-bats first, then divide.

## Interview habit
Before writing, say "one row per what?" ("one row per player"). That sentence tells you the GROUP BY column.
