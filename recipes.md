# Recipes

**Scope:** six whole jobs, each small enough
to type and each built only from moves the
earlier chapters captured. Work in
`examples/`, specimens at `data/…`.

## 1. The quarter in one screen

Takings, sales, and copies for the whole
shop, then by month — chapters 4 and 5 in
their working clothes:

```
SELECT count(*) AS sales, sum(qty) AS copies,
       round(sum(qty * unit_price), 2) AS takings
FROM 'data/bookshop_sales.csv';
-- 120 sales, 240 copies, 3711.81

SELECT date_trunc('month', sold_on) AS month,
       round(sum(qty * unit_price), 2) AS takings
FROM 'data/bookshop_sales.csv'
GROUP BY month ORDER BY month;
-- 2024-01-01: 1491.64 · 2024-02-01: 1258.72
-- 2024-03-01: 961.45
```

Check: the three months sum to the total —
1491.64 + 1258.72 + 961.45 = 3711.81. When
the parts and the whole disagree, believe
neither until you know why.

## 2. Best title in every genre

The window recipe from chapter 5, standing
alone: rank books inside their genre, keep
rank 1.

```
WITH per_book AS (
  SELECT c.title, c.genre,
         sum(s.qty * s.unit_price) AS takings
  FROM 'data/bookshop_sales.csv' s
  JOIN 'data/bookshop_catalogue.json' c
    ON s.book_id = c.book_id
  GROUP BY c.title, c.genre)
SELECT genre, title, round(takings, 2)
FROM per_book
QUALIFY rank() OVER (PARTITION BY genre
                     ORDER BY takings DESC) = 1
ORDER BY genre;
```

Check: six rows, one per genre, headed by
*Volcanoes of the North* at 630.00 in
Science.

## 3. A year of weather, summarised

```
SELECT count(*) AS readings,
       round(avg(temp_c), 2) AS avg_temp,
       round(min(temp_c), 1) AS coldest,
       round(max(temp_c), 1) AS hottest,
       round(sum(rain_mm), 1) AS rain_mm
FROM 'data/weather_readings.csv';
```

Check: 8,784 readings and 5,403.4 mm of
rain, as captured; the count is the check
that matters — if your copy of the file
answers anything else, it is not the lab
file.

## 4. Convert a CSV you trust to Parquet

```
COPY (SELECT * FROM 'data/weather_readings.csv')
TO 'exports/weather.parquet' (FORMAT PARQUET);
SELECT count(*) FROM 'exports/weather.parquet';
```

Check: the count matches the source (8,784)
and the Parquet is roughly a third of the
CSV's bytes (83,073 against 275,981 here;
your ratio will differ with your data). From
now on, query the Parquet and keep the CSV
as the archive of record.

## 5. Rescue a mixed-format date column

The chapter 3 pattern as a recipe: parse by
each candidate format in turn, keep the first
that fits, and — this is the step people
skip — count what failed:

```
SELECT count(*) AS rows_total,
       count(arrived) AS rows_parsed
FROM (
  SELECT coalesce(
    try_strptime(arrived_on, '%Y-%m-%d'),
    try_strptime(arrived_on, '%d/%m/%Y'),
    try_strptime(arrived_on, '%Y/%m/%d'),
    try_strptime(arrived_on, '%B %d, %Y'),
    try_strptime(arrived_on, '%d-%m-%Y')) AS arrived
  FROM 'data/mixed_dates.csv');
-- 8 total, 8 parsed
```

Check: parsed equals total before you build
anything on the dates. A shortfall is a
format you haven't met yet, sitting in the
rows the `coalesce` left NULL.

## 6. The same questions, from Python

Chapter 10 explains why you might; here is
the whole of it. The library is the same
engine — the guide's one Python capture
produced identical answers to the CLI:

```
$ python3 python_demo.py
Travel: 60
Fiction: 50
Science: 50
History: 40
Cookery: 30
Craft: 10
rain in 2024, mm: 5403.4
```

from a script whose moving parts are three:

```python
import duckdb
con = duckdb.connect()              # in-memory
rows = con.execute("SELECT ...").fetchall()
```

`duckdb.connect('shop.duckdb')` opens the
persistent file instead — with the same
one-writer lock chapter 7 proved at the CLI.
