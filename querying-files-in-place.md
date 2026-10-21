# Querying Files in Place

**Scope:** the one move the whole tool is
built around — a file's path written where a
table name would go — the explicit readers
behind it, and how to ask what shape DuckDB
thinks your file is.

## The filename is the table

In ordinary SQL, `FROM` names a table that
lives inside a database. In DuckDB, it can
name a **file** instead, quoted as a string:

```
$ duckdb -c "SELECT count(*) AS sales_rows FROM 'data/bookshop_sales.csv';"
┌────────────┐
│ sales_rows │
│   int64    │
├────────────┤
│        120 │
└────────────┘
```

One hundred and twenty — the lab notes'
promised count, with no import, no staging
table, and nothing created on disk. DuckDB
looked at the extension, chose its CSV
reader, worked out the columns, and answered.
The same spelling works for the other two
formats this guide uses:

```
SELECT * FROM 'data/bookshop_catalogue.json';
SELECT * FROM 'exports/weather.parquet';
```

and behind the shorthand sit the explicit
reader functions, which accept options the
shorthand cannot — chapter 3 lives on their
option lists:

```
SELECT * FROM read_csv('data/bookshop_sales.csv');
SELECT * FROM read_json('data/bookshop_catalogue.json');
SELECT * FROM read_parquet('exports/weather.parquet');
```

DuckDB also tolerates the clauses in the
other order, `FROM` first, which some people
find reads better for long queries. Both are
captured in this guide; they are the same
query:

```
$ duckdb -c "FROM 'data/bookshop_sales.csv' SELECT till_no, count(*) AS sales GROUP BY till_no ORDER BY till_no;"
┌─────────┬───────┐
│ till_no │ sales │
│  int64  │ int64 │
├─────────┼───────┤
│       1 │    40 │
│       2 │    40 │
│       3 │    40 │
└─────────┴───────┘
```

Forty sales per till — the generator dealt
them evenly, and now you have a way to prove
claims like that instead of believing them.

## Nothing was imported

Say it plainly, because every habit from
other databases argues the opposite: **the
file is re-read by every query.** The "table"
exists only for the length of the query that
names the file. Edit the file and the next
query sees the edit. The proof, on a *copy*
of the sales file with one row appended:

```
$ duckdb -c "SELECT count(*) AS rows_after_edit FROM 'exports/sales_edited.csv';"
┌─────────────────┐
│ rows_after_edit │
│      int64      │
├─────────────────┤
│             121 │
└─────────────────┘
```

This cuts both ways, and both ways matter.
There is no stale snapshot to confuse you and
no load step to forget — and there is also no
index, no stored statistics, nothing kept.
Ask the same question a hundred times and the
file is read a hundred times. Chapter 6 is
about the day that starts to matter, and
chapter 7 about tables that persist on
purpose.

## Ask what shape it chose

Because the reader *guesses* — the delimiter,
the header row, every column's type — the
second habit to form is asking what it
guessed. `DESCRIBE` over the same `SELECT`
shows the schema DuckDB settled on:

```
$ duckdb -c "DESCRIBE SELECT * FROM 'data/bookshop_sales.csv';"
┌─────────────┬─────────────┬─────────┬─────────┬─────────┬─────────┐
│ column_name │ column_type │  null   │   key   │ default │  extra  │
│   varchar   │   varchar   │ varchar │ varchar │ varchar │ varchar │
├─────────────┼─────────────┼─────────┼─────────┼─────────┼─────────┤
│ sale_id     │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ sold_on     │ DATE        │ YES     │ NULL    │ NULL    │ NULL    │
│ book_id     │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ shelf_code  │ VARCHAR     │ YES     │ NULL    │ NULL    │ NULL    │
│ qty         │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ unit_price  │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ till_no     │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
└─────────────┴─────────────┴─────────┴─────────┴─────────┴─────────┘
```

Read that table the way you'd read a
weather forecast: `sold_on` became a real
`DATE`, not text — good. `shelf_code` stayed
`VARCHAR` — the leading zeros survived, and
chapter 3 explains both why that was luckier
than it looks and how quickly it can go
wrong. `unit_price` became `DOUBLE` — hold
that thought until chapter 3 as well.

For the JSON catalogue, the same question:

```
$ duckdb -c "DESCRIBE SELECT * FROM 'data/bookshop_catalogue.json';"
book_id     BIGINT
title       VARCHAR
author      VARCHAR
genre       VARCHAR
list_price  DOUBLE
shelf_code  VARCHAR
```

(shown compactly; the full table is in the
transcripts). JSON's own types carry most of
the answer — strings stay strings, numbers
stay numbers — which is why the catalogue's
`shelf_code` was never in danger.

A second opinion is one word away.
`SUMMARIZE` runs the file and reports the
shape of the *values*: minimum, maximum,
approximate distinct count, average, null
percentage, per column. The sales file's
summary confirms, among other things, that
`shelf_code` runs from `0007` to `0107` with
12 distinct values — zeros intact — and that
nothing in the file is null. The full capture
is wide (twelve statistics per column) and
lives in `duckdb-lab/transcripts/`; run it
yourself and read it at your terminal's pace.

Check: the two questions to ask of any file
before you trust an answer from it —

```
DESCRIBE SELECT * FROM 'the-file';   -- what types?
SELECT count(*) FROM 'the-file';     -- how many rows?
```

— and compare the count against what the
file's owner told you, or against `wc -l`
minus the header. A mismatch is never a
rounding error; it is chapter 11 knocking.
