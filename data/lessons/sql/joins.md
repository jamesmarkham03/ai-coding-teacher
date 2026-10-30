# Joins

A **join** combines rows from two tables using a matching column, usually a foreign key like `players.team_id = teams.id`.

## Key ideas
- **INNER JOIN** (or just JOIN): only rows that match on both sides.
- **LEFT JOIN**: every row from the left table; right-side columns are NULL where nothing matched.
- **Aliases**: `FROM players p JOIN teams t ON p.team_id = t.id` keeps long names short and avoids ambiguity.
- **Anti-join** (rows with NO match): `LEFT JOIN ... WHERE right.id IS NULL`. For example, teams with no players.
- **NULL never matches**: a player with `team_id = NULL` disappears from an INNER JOIN.
- **Watch for duplicates**: if one team has 3 players, a join repeats the team row 3 times.

## Example
```sql
SELECT p.name, t.name AS team
FROM players p
LEFT JOIN teams t ON p.team_id = t.id;
```
Every player appears. `team` is NULL for players without one.

## Interview habit
Start by naming the two tables and the column that links them. Then decide: "Do I want to keep rows that don't match?" If yes, LEFT JOIN. If you only want matches, INNER JOIN.
