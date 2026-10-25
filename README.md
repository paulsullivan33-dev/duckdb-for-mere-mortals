# DuckDB for Mere Mortals

The sibling guide *SQL for Mere Mortals*
teaches the language: SELECT, WHERE, JOIN,
GROUP BY. This guide teaches one engine to
run it in — **DuckDB**, the analytical
database that is not a server. There is
nothing to install beyond one program, no
port, no accounts: DuckDB runs inside your
own session and answers SQL over files you
already have. A CSV, a JSON document, a
Parquet file can be named where a table name
would go and queried on the spot, and when
tables must persist, a database lives in a
single file you open by name.

DuckDB's reputation is for speed, and this
guide is not interested in it. What makes the
tool worth a guide is a shape: the shortest
honest path from "I have files and questions"
to answers you can check, with the guessing —
and DuckDB guesses constantly, about types,
about date formats, about what your CSV even
is — dragged into the light and verified
against specimen data whose answers are known
before the query runs.

The lab is one folder of data files, built
by a script in `examples/` (`build-lab.py`):
an invented bookshop's 120 sales and its
12-book catalogue as JSON, one weather
station's 8,784 hourly readings for leap
year 2024, a small stock file whose dates
arrive in four different formats, and a
five-row extract with two damaged rows.
Every name is invented and every count is
deliberate.

A note on how this guide was verified.
DuckDB 1.4.1 (Andium) was run on the build
machine, and every command quoted was run
against the lab files and captured: the
answers, the counts, the timings, the lock
refusal, and the failures — including one
failure of the author's own (a connection
string handed to the CLI as a filename) that
chapter 7 confesses. Where a behaviour is
this version's rather than a law, the
chapters say so, and `criteria.md` keeps the
ledger of what is documented-only.

## What this guide covers

- [**What DuckDB is**](what-duckdb-is.md) —
  two shapes of question, an engine in your
  process, the one-writer limit stated up
  front, your version, and the lab
- [**Querying files in place**](querying-files-in-place.md) —
  the filename as table, the explicit
  readers, proof that nothing was imported,
  and asking what shape it chose
- [**When it guesses wrong**](when-it-guesses-wrong.md) —
  the sniffer, codes stripped of their
  zeros, money as DOUBLE, a file with four
  date formats, and the casting tools that
  fix them
- [**Joins across files**](joins-across-files.md) —
  one question over a CSV and a JSON file,
  aliases, and why keys must agree before
  rows can
- [**Aggregates and windows**](aggregates-and-windows.md) —
  `GROUP BY` collapsing rows, window
  functions keeping them: ranks within
  groups and running totals
- [**Writing results out**](writing-results-out.md) —
  `COPY TO` in CSV, JSON, and Parquet, the
  measured size difference, and a timing
  quoted with its health warning
- [**Databases that persist**](databases-that-persist.md) —
  the `.duckdb` file, in-memory contrast,
  the one-writer lock proven, and read-only
  company
- [**The CLI around the SQL**](the-cli-around-the-sql.md) —
  dot-commands: `.mode`, `.headers`,
  `.output`, `.schema`, `.timer`, each
  checked against 1.4.1's own `.help`
- [**Recipes**](recipes.md) — the quarter in
  one screen, the best title per genre, a
  CSV-to-Parquet conversion, a mixed-date
  rescue with its count check, and the same
  questions from Python
- [**The neighbours**](the-neighbours.md) —
  SQLite the sibling, PostgreSQL the
  server, jq, the spreadsheet, and pandas,
  each placed on its own merits
- [**Troubleshooting**](troubleshooting.md) —
  the one-column CSV, the lock, the vanished
  table, and the rest of the captured errors
  as symptom → fix
- [**Glossary**](glossary.md) — the terms,
  collected in one place

## What it doesn't cover

SQL itself — the sibling *SQL for Mere
Mortals* owns the grammar; this guide spends
its words on the engine and its files.
DuckDB's extension ecosystem (reading from
S3, spatial data, Iceberg) is named nowhere
but here: real, useful, and undemonstrated —
the lab is local files on purpose. The other
language clients (R, Node, Java, and the
rest) share the engine and differ in
plumbing; the Python library is exercised
briefly in recipe 6 and the others are
documented-only. And performance tuning —
memory limits, thread counts, partitioning
strategy — belongs to a guide about bigger
data than a specimen folder.

## How to use this guide

Read chapter 1, build the lab as it directs,
and keep a terminal in `examples/` from
chapter 2 on. The specimens are rebuilt
byte-identically by their script, so no
experiment can ruin them; the exports and
database files the chapters make are yours
to delete and remake. Keep the habit the
guide keeps repeating: DESCRIBE a file
before you trust it, and count before and
after anything that can drop rows.

## Fixture rebuild safety

The fixture builder creates a new target
directory. It replaces an existing target
only when a completed-build marker sits
beside it (`data.mere-mortals-fixture` for a
data directory named `data`). Existing
unmarked directories are refused. Older
fixture directories have no marker: use a
fresh directory name and inspect the old one
manually. Do not add a marker to an unrelated
directory.

---

## Part of the series

This guide is one of the [For Mere Mortals](https://paulsullivan33-dev.github.io/mere-mortals/) guides: plain-language guides to the tools programmers and makers use.

Related guides:

- [SQL for Mere Mortals](https://paulsullivan33-dev.github.io/sql-for-mere-mortals/)
- [SQLite for Mere Mortals](https://paulsullivan33-dev.github.io/sqlite-for-mere-mortals/)
- [jq for Mere Mortals](https://paulsullivan33-dev.github.io/jq-for-mere-mortals/)

## License

The writing in this guide is licensed under [CC BY 4.0](https://github.com/paulsullivan33-dev/duckdb-for-mere-mortals/blob/main/LICENSE). Code examples and lab scripts are licensed under the [MIT License](https://github.com/paulsullivan33-dev/duckdb-for-mere-mortals/blob/main/LICENSE-CODE).
