# Glossary

**Aggregate** — a function that takes many
rows and returns one value: `sum`, `count`,
`avg`, `min`, `max`. With `GROUP BY`, one
value per group (chapter 5).

**Analytical query** — a question about whole
tables at once: totals, averages, rankings,
joins over everything. The workload DuckDB
is shaped for; contrast *bookkeeping*.

**Bookkeeping** — the other workload: a few
rows at a time, changed all day, by many
hands. Database servers' home ground.

**CAST / TRY_CAST** — converting a value to
another type. `CAST` stops the query with an
error when a value won't convert; `TRY_CAST`
returns NULL for that value instead (chapter
3).

**Columnar** — storage laid out by column
rather than by row, so a query reads only the
columns it names. Parquet is columnar; CSV is
not.

**COPY TO** — the statement that writes a
query's result to a file as CSV, JSON, or
Parquet (chapter 6).

**CTE** — a `WITH` clause: a named subquery
written before the main query, so a result
can be built in stages (chapter 5).

**DECIMAL(10,2)** — an exact decimal type:
ten digits in all, two after the point. The
right home for money, where `DOUBLE` cannot
hold most prices exactly (chapter 3).

**DESCRIBE** — the question that reports the
columns and types DuckDB settled on for a
query or file (chapter 2).

**Dialect** — a CSV file's conventions: its
delimiter, quote character, escape, and
header row. The sniffer's first guess.

**Dot-command** — a shell instruction
beginning with `.` (`.mode`, `.schema`,
`.timer`), steering the CLI rather than the
engine (chapter 8).

**Embedded / in-process** — an engine that
runs inside your own program or terminal
session instead of as a separate server
(chapter 1). DuckDB and SQLite are embedded;
PostgreSQL is not.

**In place** — reading and querying a file
where it sits, with no import step. Every
query re-reads the file (chapter 2).

**Join** — pairing rows from two sources
where a key matches, for the length of one
query (chapter 4).

**NULL** — the absence of a value. Not zero,
not empty text; comparisons with it are
themselves NULL, and `TRY_CAST` leaves
failures as NULLs you are expected to count.

**Parquet** — a binary, columnar file format
that stores values with their schema: no
sniffing, typically a fraction of the CSV's
size, unreadable in a text editor (chapter
6).

**Partition** — the groups a window function
computes over separately: `PARTITION BY
genre` restarts the ranking inside each
genre (chapter 5).

**Persistent database** — DuckDB's tables
kept in a single `.duckdb` file between
sessions (chapter 7), as opposed to the
`:memory:` database that ends with the
process.

**QUALIFY** — the clause that filters on a
window function's result, doing for windows
what `WHERE` cannot (chapter 5).

**Schema** — the shape of data: column names
and their types. CSV leaves it to be guessed;
Parquet and a database file carry it.

**Single writer** — DuckDB's rule that one
process at a time may write a database file;
a second is refused at the lock (chapter 7).

**Sniffer** — the component that samples a
CSV file and proposes its dialect and column
types (chapter 3). Its guesses are good and
are still guesses.

**try_strptime** — parsing text into a date
or timestamp against a format *you* supply,
returning NULL when it doesn't fit (chapter
3).

**View** — a saved query stored under a
table's name in a database file; it holds no
rows and is re-run when read (chapter 7).

**Window function** — a computation over a
partition or frame of rows that adds a column
to every row instead of collapsing them:
rankings, running totals (chapter 5).
