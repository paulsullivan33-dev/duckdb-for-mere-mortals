# The CLI Around the SQL

**Scope:** the shell you have been typing at —
its dot-commands for output shape, session
inspection, and timing — with every spelling
verified against 1.4.1's own `.help`.

## Two languages in one prompt

The CLI speaks SQL, and it also speaks a
second, smaller language of commands that
begin with a dot. Dot-commands are not SQL:
they end without a semicolon, they are never
sent to the engine, and they steer the *shell*
— how results are drawn, where they go, what
the session holds. The design is inherited
from the SQLite shell, which DuckDB's CLI
follows closely; anyone who has driven
`sqlite3` will find the furniture familiar.

The full list is one command long:

```
.help ?-all? ?PATTERN?   Show help text for PATTERN
```

Run `.help` and it prints fifty-odd entries;
run `.help mode` and it filters. Everything
in this chapter was checked against that
output in 1.4.1 — dot-command spellings drift
between versions more freely than SQL does,
so `.help` on *your* binary outranks this
page.

## How results are drawn: .mode

The bordered box you have been reading is
`.mode duckbox`, the default. Two others earn
their keep immediately. `.mode list` draws
pipe-separated values, and with `.headers
off` it is plain machine-fodder:

```
.mode list
.headers off
SELECT sale_id, sold_on, qty FROM 'data/bookshop_sales.csv' LIMIT 3;
1|2024-01-02|1
2|2024-01-02|3
3|2024-01-02|2
```

`.mode json` draws the result as a JSON
array — the same shape chapter 6 wrote to a
file, at the terminal instead:

```
.mode json
SELECT sale_id, sold_on, qty FROM 'data/bookshop_sales.csv' LIMIT 2;
[{"sale_id":1,"sold_on":"2024-01-02","qty":1},
{"sale_id":2,"sold_on":"2024-01-02","qty":3}]
```

`.headers on|off` deserves its own sentence:
half the scripts that consume a query's output
break on the header row or its absence, and
this is the switch they are arguing about.
Dot-command settings last for the session;
they are not written anywhere.

## Where results go: .output

`.output exports/three_sales.txt` diverts
everything the shell prints into that file
until `.output stdout` brings it back. The
diverted file holds the result *as drawn* —
boxes and all:

```
┌─────────┬───────┐
│ sale_id │  qty  │
├─────────┼───────┤
│       1 │     1 │
│       2 │     3 │
│       3 │     2 │
└─────────┴───────┘
```

That is the dividing line with chapter 6:
`.output` saves a *picture* of the answer for
a person; `COPY TO` writes the answer as
*data* for a program. Confuse them and
somebody parses box-drawing characters at
midnight.

## What the session holds

Inside a database session (chapter 7's file,
or an in-memory one where you have created
things), three commands report on the state:

```
.tables            → sales            (the names)
.schema sales      → CREATE TABLE sales(sale_id BIGINT,
                       sold_on DATE, book_id BIGINT,
                       shelf_code VARCHAR, qty BIGINT,
                       unit_price DOUBLE, till_no BIGINT);
```

`.schema` handing you back the table's own
definition — column types included — is the
quickest way to check what a `CREATE TABLE AS`
actually stored, and whether chapter 3's
types survived the trip.

## Timing: .timer

`.timer on` appends one line after each
query:

```
Run Time (s): real 0.044 user 0.036890 sys 0.004833
```

`real` is the wall clock; `user` and `sys`
are CPU time in your process and in the
kernel on its behalf. Chapter 6's CSV-versus-
Parquet pair was measured with exactly this
line, once per side — and its health warning
lives there too: a single timing of a fast
query is a weather report, not a climate.
Run a timing several times before believing
its second digit.
