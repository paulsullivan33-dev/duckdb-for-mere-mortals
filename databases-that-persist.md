# Databases That Persist

**Scope:** the other mode — a database kept
in a single `.duckdb` file, tables that
survive between sessions, and the one-writer
limit proven at the lock instead of merely
asserted.

## Name a file, get a database

Start the CLI with a filename instead of
nothing:

```
$ duckdb lab.duckdb
```

and everything you create now persists into
that one file. Populate it from the specimens
with `CREATE TABLE … AS` over an ordinary
in-place query:

```
$ duckdb lab.duckdb -c "CREATE TABLE sales AS FROM 'data/bookshop_sales.csv'; CREATE VIEW shelf AS SELECT shelf_code, count(*) AS sales FROM sales GROUP BY shelf_code; SHOW TABLES;"
┌─────────┐
│  name   │
│ varchar │
├─────────┤
│ sales   │
│ shelf   │
└─────────┘
$ ls -l lab.duckdb
-rw-rw---- 1 root nogroup 536576 ... lab.duckdb
```

A **view**, the second object there, stores
no rows — it is a saved query wearing a
table's name, re-run each time it is read.
The file itself is 536,576 bytes: the 120
sales rows, the view's definition, and the
storage format's overhead, in one portable
file you can copy like any other.

Close the program, reopen the file, and the
tables are simply there:

```
$ duckdb lab.duckdb -c "SELECT count(*) AS sales_rows FROM sales;"
120
```

Contrast the bare invocation. `duckdb` with
no filename opens `:memory:` — a database
that lives only inside that one process. In
one session a table can be created and read;
in the very next invocation it has never
existed:

```
first session:   CREATE TABLE t AS SELECT 1 AS x;
                 SELECT count(*) FROM t;   → 1
second session:  SELECT count(*) FROM t;
Catalog Error: Table with name t does not exist!
```

Neither mode is the "real" one. In-memory is
for questions; a file is for keeping. The
mistake is only ever confusing which one you
are in — the error above is how the confusion
announces itself, and chapter 11 files it
under troubleshooting.

## One writer: the lock is the lesson

Chapter 1 promised this limit in plain terms;
here it is at the metal. Hold `lab.duckdb`
open in one process, and ask a second process
to open the same file for writing:

```
$ duckdb lab.duckdb -c "SELECT count(*) FROM sales;"
Error: unable to open database "lab.duckdb":
IO Error: Could not set lock on file "lab.duckdb":
Conflicting lock is held in .../duckdb (PID 11952).
See also https://duckdb.org/docs/stable/concurrency
[exit 1]
```

Not a queue, not a merge, not a warning: a
refusal, naming the process that holds the
lock. This is the price of the zero-admin
engine, charged exactly where chapter 1 said
it would be. Readers, though, are cheap.
Opened **read-only**, the same file admits
company — two simultaneous read-only
connections, each counting the same table:

```
$ duckdb -readonly lab.duckdb -c "SELECT count(*) AS a FROM sales;" &
$ duckdb -readonly lab.duckdb -c "SELECT count(*) AS b FROM sales;"
a → 120        b → 120
```

A read-only connection cannot change
anything, and it also cannot see changes made
after it opened — it reads the file as it
was. For looking, that is usually exactly
right.

So the working rules for a `.duckdb` file:

- **One program writes; everyone else reads
  read-only, or waits.** A nightly job that
  rebuilds a database file and daytime queries
  that open it `-readonly` is a perfectly
  respectable architecture.
- **A database file is not a shared drive
  free-for-all.** Two machines opening the
  same file over a network share are outside
  what the lock can protect; the lock lives
  on one machine.
- **When two writers must truly work at
  once**, the answer is not a bigger DuckDB;
  it is a database server. Chapter 10 says
  which and why.

A closing trap from this guide's own build,
declared in `criteria.md`: at the command
line, the file is named plainly —
`duckdb -readonly lab.duckdb`. The
`file.duckdb?access_mode=read_only` spelling
belongs to the client libraries' connection
strings; handed to the CLI in 1.4.1 it is
taken as a literal filename, and DuckDB
cheerfully creates an *empty database under
that long strange name*. If a directory ever
contains a file with `?` in its name, that is
what happened.
