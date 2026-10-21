# Writing Results Out

**Scope:** `COPY TO` — turning a query's
answer into a file of your own, in CSV, JSON,
and Parquet — and the measured difference
the format makes.

## An answer you can keep

Every query so far ended at the terminal.
`COPY (query) TO 'file'` runs the query and
writes its result as a file instead:

```
$ duckdb -c "COPY (SELECT c.genre, sum(s.qty) AS copies FROM 'data/bookshop_sales.csv' s JOIN 'data/bookshop_catalogue.json' c ON s.book_id = c.book_id GROUP BY c.genre) TO 'exports/by_genre.csv' (HEADER);"
$ ls -l exports/by_genre.csv
-rw-rw---- 1 root nogroup 76 ... exports/by_genre.csv
```

(the mode and owner on that listing are the
build machine's weather, not a property of
the file). Seventy-six bytes: six genres and
their copy counts, with a header row because
`(HEADER)` asked for one. The same query to
JSON is one option different:

```
COPY (SELECT ...) TO 'exports/by_genre.json' (FORMAT JSON, ARRAY true);
[
	{"genre":"Fiction","copies":50},
	{"genre":"Travel","copies":60},
	{"genre":"Craft","copies":10},
	...
]
```

`(ARRAY true)` asks for one JSON array of
objects; without it, DuckDB writes
newline-delimited JSON, one object per line —
the shape most other tools expect. Neither
is wrong; they are different contracts, and
the difference is invisible until a reader
chokes on it, so say which one you wrote.

An export is a **snapshot**. It does not stay
in step with the files it was computed from;
chapter 2's rule — every query re-reads its
files — applies to the *next* query, not to
the copy you already wrote. Rerun the `COPY`
to refresh it, and treat any export older
than the data it came from as a historical
document.

## Parquet: the format that keeps its answers

CSV stores text and lets every reader guess.
**Parquet** stores typed columns — the values
*and* their schema, in a columnar layout
built for exactly the whole-table questions
of chapter 1. Converting the weather file is
the same `COPY` with a different format, and
the sizes are the argument:

```
$ wc -c data/weather_readings.csv exports/weather.parquet
275981 data/weather_readings.csv
 83073 exports/weather.parquet
```

Same 8,784 rows — proven by counting the
Parquet straight back:

```
$ duckdb -c "SELECT count(*) AS rows_in_parquet FROM 'exports/weather.parquet';"
8784
```

The Parquet file is 30% of the CSV's size,
because repeated timestamps and smooth
temperature series compress well when stored
column by column. It also asks the sniffer
nothing: `DESCRIBE` over the Parquet returns
`read_at TIMESTAMP`, `temp_c DOUBLE`,
`humidity_pct BIGINT`, `rain_mm DOUBLE` —
the types were written into the file, not
re-derived from a sample.

The honest cost side: Parquet is binary. You
cannot read it in a text editor, diff it
meaningfully, or fix a row with `sed`. CSV's
clumsiness is also its transparency. Choose
per file, not per worldview.

## Speed, measured and qualified

With `.timer on` (chapter 8), the year's
average temperature and total rain, once per
source, on the build machine:

```
from the CSV:      Run Time (s): real 0.044
from the Parquet:  Run Time (s): real 0.014
```

Both are effectively instant — at 8,784 rows
everything is instant — so read those numbers
the way criterion 4 insists: one run each, on
one machine, at a size where the difference
cannot matter yet. What generalises is the
*shape*: the CSV was parsed from text, all
8,784 rows, types re-guessed; the Parquet was
read as typed columns, and only the two
columns the query named. The gap between
those two costs grows with the file. At a
hundred million rows it is the difference
between a coffee break and a sigh — but that
sentence is experience talking, not a
measurement, and this guide labels it as
such.

Check: the export checklist —

```
1. COPY's query is the deliverable: run it
   plain first, read the answer, then wrap it.
2. Count the export back (chapter 2's habit).
3. Write down the format options you used —
   (HEADER), (ARRAY true) — beside the file,
   not in your head.
```
