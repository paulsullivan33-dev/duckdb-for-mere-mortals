# What DuckDB Is

**Scope:** the mental model — a SQL engine that
runs inside your own tools instead of on a
server, built for questions about whole tables
at once — plus your version, and the lab.

## Two shapes of question

Databases earn their keep answering two quite
different shapes of question. One is
**bookkeeping**: record this sale, find that
one customer's order, change this one address.
A few rows at a time, all day long, from many
people at once. The other shape is
**analysis**: total the year's sales by genre,
average a year of hourly temperatures by
month, rank every book against the others in
its section. Whole tables at a time, usually
by one person, usually read-only.

Most famous databases are shaped for the
first kind. **DuckDB** is shaped for the
second. It speaks full SQL — joins, grouping,
window functions, the lot — and it runs
**in-process**: there is no server to install,
no port to open, no account to create. You run
the `duckdb` program (or load the library
inside Python, R, and other languages) and the
engine is simply *there*, in the same way a
calculator is there. This guide teaches the
command-line program; chapter 10 places the
neighbours it borrows ideas from.

The other half of the idea: DuckDB's favourite
input is **files you already have**. A CSV, a
JSON document, a Parquet file — each can be
named in a query exactly where a table name
would go, and DuckDB reads it on the spot:

```
SELECT count(*) FROM 'data/weather_readings.csv';
```

No import step, no staging table, no copy.
Chapter 2 lives on that one move. When you do
want tables that persist, DuckDB offers those
too: a database kept in a single file, opened
with `duckdb shop.duckdb`, chapter 7. The two
modes share one engine and one SQL.

## The honest limit, up front

An engine that runs inside your process can
make a promise a server never could — zero
administration — and it pays for it with a
limit this guide will not bury: **one writer
at a time**. A DuckDB database file admits a
single process writing to it; a second writer
is refused with a lock error, and chapter 7
shows that refusal verbatim. Reading files in
place has no such lock, but the moment several
people or programs must change the same data
at once, you want a database *server* —
PostgreSQL and its kin, placed honestly in
chapter 10. DuckDB is not a small or failed
server. It is a different tool, the way a
calculator is not a failed spreadsheet.

Check: the tool, on the build machine — one
downloaded binary, nothing installed
system-wide, nothing running in the
background:

```
$ duckdb --version
v1.4.1 (Andium) b390a7c376
```

Everything quoted in this guide was run with
that version. DuckDB moves quickly, and minor
versions adjust defaults and error wording;
where a behaviour is this version's rather
than a law of nature, the chapters say so.

## The lab

Everything happens over one folder of
specimen files, built by a script so your
copy is identical to the one in the captures.
From the repo root:

```
$ cd examples
$ python3 build-lab.py data
bookshop_sales.csv: 120 rows
bookshop_catalogue.json: 12 rows
weather_readings.csv: 8784 rows
mixed_dates.csv: 8 rows
broken.csv: 5 rows
built data
```

The specimens, described fully in
`examples/lab-notes.txt`: an invented
bookshop's 120 sales and its 12-book
catalogue (as JSON, deliberately a different
format from the sales CSV); one weather
station's hourly readings for the whole of
leap year 2024 — 8,784 rows; a small stock
file whose dates arrive in four different
formats; and a five-row sales extract with
two damaged rows. Every name, shop, book,
and reading is invented, and every count is
deliberate, so the chapters can promise exact
answers and then be checked against them.

Work from the `examples/` folder throughout
the guide, so the specimens are always at
`data/…` from where you stand. And keep one
distinction in mind from the start: the
specimens stay specimens. Chapter 2's whole
point is that DuckDB will happily query your
*real* files in place too — point it at the
real ones only once you have seen, on these,
what a careless query can and cannot do.
