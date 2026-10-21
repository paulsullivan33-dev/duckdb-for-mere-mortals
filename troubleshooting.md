# Troubleshooting

**Scope:** the failures this guide actually
met, each as symptom → cause → fix. Every
error quoted was captured from DuckDB 1.4.1
against the lab files.

## The CSV came back as one wide text column

**Symptom.** `SELECT * FROM 'data/broken.csv'`
returns a single column whose name is the
whole header line — `sale_id,sold_on,book_id,qty`
— and every row is one long string. The count
even looks right: 5.

**Cause.** The sniffer could not find any
dialect under which the file parses
consistently, and the best-scoring fallback
was "one column, no delimiter." In the lab
file, two damaged rows — one short a field,
one with an unclosed quote — were enough.
No error is raised. **This is the most
dangerous failure in the guide**: the answer
is the wrong *shape*, delivered calmly.

**Fix.** `DESCRIBE` any file before trusting
it (chapter 2's habit exists precisely for
this). Then look at the file with your eyes —
the damage in `broken.csv` is visible in a
text editor in seconds. To make the reader
loud instead of silent, pin the schema
(chapter 3): a forced-columns read of the same
file refuses with `It was not possible to
automatically detect the CSV parsing dialect`
and a list of suggested fixes.

## I need the good rows out of a damaged file

**Symptom.** The file is mostly fine, two
rows are broken, and every strict read fails.

**Fix.** `ignore_errors=true` on the typed
read skips what it cannot parse:

```
read_csv('data/broken.csv',
  columns={'sale_id': 'BIGINT', 'sold_on': 'DATE',
           'book_id': 'BIGINT', 'qty': 'BIGINT'},
  delim=',', ignore_errors=true)
→ rows 1, 3, 5 — typed, correct, and the
  two damaged rows simply absent
```

Then **count**: 3 rows returned against the
file's 5 data rows. `ignore_errors` never
reports what it dropped; the missing rows are
your responsibility to notice and to chase
back to whoever produced the file.

## "Could not set lock on file"

**Symptom.**

```
IO Error: Could not set lock on file "lab.duckdb":
Conflicting lock is held in .../duckdb (PID 11952)
```

**Cause.** Another `duckdb` process (the
error names its PID) holds the database file
open for writing. The file admits exactly
one writer — chapter 7.

**Fix.** Find the holder (it is usually your
own other terminal) and close it; or, if you
only need to look, open `-readonly` — as many
readers as you like, none of them able to
change anything.

## "Table with name t does not exist!"

**Symptom.** A table you definitely created
is gone.

**Cause.** You created it in an in-memory
session (`duckdb` with no filename), and that
process ended. `:memory:` keeps nothing —
chapter 7's contrast, captured verbatim.

**Fix.** Recreate it, or work in a named file
when the tables must outlive the session. No
recovery exists for the in-memory one; it was
never written anywhere.

## "Referenced column … not found"

**Symptom.**

```
Binder Error: Referenced column "titel" not found
in FROM clause! Candidate bindings: "title",
"shelf_code", "list_price"
```

**Cause.** Almost always a typo — and the
error is on your side, listing the columns
that *do* exist. Read the candidates before
reaching for anything else; chapter 3's
partial-`columns={}` failure wears the same
family resemblance (the column you asked
about exists, the ones you *didn't* name in
the map are what is missing).

## "No files found that match the pattern"

**Symptom.** `IO Error: No files found that
match the pattern "data/no_such_file.csv"`.

**Cause.** The path in quotes is a *pattern*,
and nothing on disk matches it — a typo, a
wrong working directory, or a file that was
never created.

**Fix.** `ls` the path. Most instances of
this error in the guide's own build were the
author standing in the wrong folder; the
guide assumes `examples/` from chapter 1 on.

## Totals ending in …999999997

**Symptom.** A money sum prints
`3711.809999999997` instead of `3711.81`.

**Cause.** The column was inferred (or
stored) as `DOUBLE`, and binary floating
point cannot hold most decimal prices
exactly — chapter 3.

**Fix.** Pin the column `DECIMAL(10,2)` in
`read_csv`'s `columns={}`, or cast at the
source. `round()` on the output hides the
symptom for display and fixes nothing.

## Dates that sort in the wrong order

**Symptom.** Dates come out ordered
`01/03/2024, 07-03-2024, 11/03/2024, 2024-03-01…`

**Cause.** They are text, and text sorts
alphabetically. The column's type will say
`VARCHAR` — check with `DESCRIBE`.

**Fix.** Parse them into real dates with
`try_strptime` per format (chapter 3, recipe
5), and count the NULLs it leaves.

## A strange file with a "?" in its name

**Symptom.** The directory contains a file
literally named `shop.duckdb?access_mode=read_only`,
and the real database seems empty.

**Cause.** A connection-string URI was handed
to the CLI as a filename (chapter 7). DuckDB
created a new, empty database under that
name.

**Fix.** Delete the impostor file, and at the
CLI use the flag: `duckdb -readonly shop.duckdb`.
