# Aggregates and Windows

**Scope:** the two ways SQL summarises —
`GROUP BY`, which collapses rows into one
row per group, and window functions, which
keep every row and add a column computed
over its neighbours.

## GROUP BY: fewer rows out than in

An **aggregate** takes many rows and returns
one value: `sum`, `count`, `avg`, `min`,
`max`. With `GROUP BY`, it returns one value
*per group*. The shop's quarter, by month:

```
$ duckdb -c "SELECT date_trunc('month', sold_on) AS month, count(*) AS sales, round(sum(qty * unit_price), 2) AS takings FROM 'data/bookshop_sales.csv' GROUP BY month ORDER BY month;"
┌────────────┬───────┬─────────┐
│   month    │ sales │ takings │
│    date    │ int64 │ double  │
├────────────┼───────┼─────────┤
│ 2024-01-01 │    45 │ 1491.64 │
│ 2024-02-01 │    45 │ 1258.72 │
│ 2024-03-01 │    30 │  961.45 │
└────────────┴───────┴─────────┘
```

One hundred and twenty rows in, three out.
`date_trunc('month', sold_on)` cuts each date
down to its month's first day, which is what
makes the grouping key: every January sale
carries `2024-01-01` and collapses together.

The weather file gives the same shape at
scale — 8,784 hourly readings into twelve
monthly rows (capture 20 in full). January
holds 744 readings and December 744, because
31 days × 24 hours is 744; February, in leap
year 2024, holds 696 = 29 × 24. When a group
count can be checked against the calendar,
check it. An aggregate that returns 8,783
rows' worth of readings has lost one
somewhere, and it will not tell you where.

## Windows: every row stays

Grouping throws the detail away on purpose.
Sometimes the detail is the point and the
summary is a *column on it*: each book's
takings, next to its rank **within its own
genre**. A **window function** computes over
a *partition* of the rows — here, one genre
at a time — without collapsing anything:

```
WITH per_book AS (
  SELECT c.title, c.genre,
         sum(s.qty * s.unit_price) AS takings
  FROM 'data/bookshop_sales.csv' s
  JOIN 'data/bookshop_catalogue.json' c
    ON s.book_id = c.book_id
  GROUP BY c.title, c.genre)
SELECT genre, title, round(takings, 2) AS takings,
       rank() OVER (PARTITION BY genre
                    ORDER BY takings DESC) AS rnk
FROM per_book QUALIFY rnk = 1 ORDER BY genre;
```

```
Cookery   The Winter Apiary      301.94   1
Craft     Knots and Their Uses    98.90   1
Fiction   The Glass Observatory  279.80   1
History   Empires of Salt        516.78   1
Science   Volcanoes of the North 630.00   1
Travel    The Salt Road Atlas    423.24   1
```

(shown compactly; the full table is capture
18). Three new pieces of grammar, each doing
one job. The `WITH` clause (a **CTE**) names
the per-book totals so the outer query can
rank them — the grouped half of the pattern,
reused. `rank() OVER (…)` is the window:
`PARTITION BY genre` restarts the ranking
inside each genre, `ORDER BY takings DESC`
says what rank 1 means. `QUALIFY` filters on
the window's result, which `WHERE` cannot do
— a window is computed after `WHERE` has
already run — so DuckDB gives the filter its
own clause.

A running total is the other canonical
window: no partition, and the frame is
"every day up to and including this one."

```
WITH daily AS (
  SELECT read_at::DATE AS day,
         round(sum(rain_mm), 1) AS rain
  FROM 'data/weather_readings.csv' GROUP BY day)
SELECT day, rain,
       round(sum(rain) OVER (ORDER BY day), 1) AS rain_so_far
FROM daily LIMIT 10;
```

```
2024-01-01   25.3    25.3
2024-01-02    6.9    32.2
2024-01-03   24.1    56.3
2024-01-04    6.1    62.4
2024-01-05   16.7    79.1
... (366 rows in all; first five of ten shown)
```

`sum(rain) OVER (ORDER BY day)` — the same
`sum` as any aggregate, but the window frame
makes it sum a *prefix* of the rows for each
row's column instead of collapsing to one
number. The year's rain, 5,403.4 mm by the
aggregate's reckoning (capture 24), is simply
the last row of this column.

## Which one, when

Ask what happens to the rows. If the answer
is "one row per group," it's `GROUP BY`. If
the answer is "all the rows, each carrying
something computed from its group or its
neighbours," it's a window. The confusion to
avoid is reaching for a window to do a
group's job or vice versa; both compute sums,
and the difference is entirely in what
survives.
