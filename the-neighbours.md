# The Neighbours

**Scope:** the tools DuckDB is mistaken for,
and the honest line around each: SQLite,
PostgreSQL, jq, a spreadsheet, and pandas.
What each keeps, what each gives back.

## SQLite: the sibling

SQLite is the other embedded SQL engine, and
the resemblance is not a coincidence of
purpose but of architecture: a library, a
single file for a database, no server. The
CLI's dot-commands are inherited from
SQLite's shell outright. The difference is
the shape of question each was built for.
SQLite stores rows and serves **bookkeeping**
— the point-of-sale till recording sales all
day, an app keeping its state — and it allows
exactly the write-heavy, small-transaction
workload DuckDB declines. DuckDB stores and
scans **columns** and serves analysis over
whole tables. Same SQL accent, different
trades. If your program needs a database
*inside itself* to remember things, SQLite is
the default answer and a good one; if it
needs to *summarise* a million rows, that is
DuckDB's chair.

## PostgreSQL: the server

PostgreSQL is everything chapter 7 said
DuckDB is not: a server process, accounts and
permissions, many readers *and* many writers
at once, clients connecting over a network.
When the one-writer lock is your problem —
several people or programs changing shared
data all day — PostgreSQL is not an upgrade
to DuckDB; it is the correct tool, and
migrating to it is a promotion of the data,
not a failure of the prototype. The costs are
real and are the mirror of DuckDB's virtues:
something to install, run, back up, and
administer. Earn them when the sharing is
real.

## jq: the pocket knife

For a quick look inside one JSON document —
pretty-print it, pull one field, count the
array — `jq` answers in one command with no
schema ceremony, and this guide's catalogue
file is small enough that `jq` would serve
most first questions about it. jq stops being
the right tool where the questions turn
relational: joins against another file,
grouped totals, anything where "the JSON" is
really a table wearing a costume. DuckDB
reads the same file as a table and the SQL
machinery takes over. Pocket knife versus
workbench; the honest answer is that a bench
needs both.

## The spreadsheet

A spreadsheet is the analysis tool most
people already have, and for a few hundred
rows and a question asked once, it is
genuinely fine — open the CSV, eyeball it,
done. Its limits arrive quietly: the file
gets big, the question gets asked every
week, a column's type is whatever the import
wizard felt like, and the answer lives in a
grid of manual steps nobody can re-run or
audit. A DuckDB query is the opposite
profile: a line of text that *is* the method,
re-runnable against next month's file by
changing one filename. When a spreadsheet
analysis becomes a ritual, it is asking to
be rewritten as a query.

## pandas

pandas is Python's data-frame library — the
analysis tool most Python programmers reach
for, and the one DuckDB coexists with rather
than replaces. Load a CSV into pandas and the
whole thing sits in memory as dataframes you
manipulate in Python; ask DuckDB and the SQL
engine does the joining and grouping, handing
back results that pandas can take over. The
two interoperate directly (DuckDB can query a
dataframe as if it were a table), and the
guide's one Python capture (recipe 6) is the
shape of it. Choose by where the question
lives: already inside a Python program, with
Python-shaped follow-up work — pandas, or
DuckDB from inside the program. Sitting at a
terminal with files and questions — the CLI,
and this guide.

| Tool | Runs as | Writers | Best question |
|---|---|---|---|
| DuckDB | in-process | one | "total/average/rank over this whole file" |
| SQLite | in-process | one at a time, built for it | "remember this, inside my app" |
| PostgreSQL | server | many | "everyone's data, changed all day" |
| jq | one-shot filter | n/a | "what's inside this one JSON?" |
| Spreadsheet | application | one person | "let me look at a few hundred rows" |
| pandas | Python library | one program | "analyse this, inside my program" |
