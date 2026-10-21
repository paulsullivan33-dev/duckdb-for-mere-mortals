# Writing Criteria

Every guide in this repo is written to the same
standard. If you're adding or editing a guide —
human or AI — hold it to these.

1. **Plain words, real ideas.** Simple language,
   never dumbed-down concepts. Explain jargon on
   first use; collect terms in the glossary.
2. **No hype.** No marketing adjectives, no
   "revolutionary," no promises about what
   something will do for the reader.
3. **Honest about limits.** Say what the thing
   *can't* do. State uncertainty instead of
   smoothing it over. Validation notes include
   what remains unverified.
4. **No invented numbers.** Benchmarks, defaults,
   and specs are either measured or qualified with
   "depends on your setup." If it wasn't tested,
   say so.
5. **Checkable.** Commands are meant to be run,
   with "Check:" blocks showing what success looks
   like. Sources are linked, not asserted.
6. **Respect the reader's setup.** Call out
   Windows/Mac/Linux differences. Don't assume a
   GPU, a budget, or prior experience.
7. **Safety isn't skipped.** Real risks get
   stated plainly, not buried.
8. **Scoped.** Each guide says what it covers and
   points elsewhere for the rest. No guide
   pretends to be the whole subject.
9. **Structure over prose.** Tables, before/after
   examples, symptom → fix. Scannable beats essay.

## Verification notes for this guide

Standard 3 and 4 applied to this guide,
specifically. The build machine ran Ubuntu
with **DuckDB 1.4.1 (Andium), build
b390a7c376** — the official linux-amd64 CLI
binary from the duckdb/duckdb GitHub release,
run from a workspace folder, not installed
system-wide. Every quoted output in the
chapters is a capture from that binary, run
against the specimen files. Working
transcripts are kept with the build
(`duckdb-lab/transcripts/`, 54 captures).

**The lab.** One folder of data files, built
by `examples/build-lab.py`, byte-identical on
every rebuild (seeded generation, LF line
endings): `bookshop_sales.csv` (120 rows),
`bookshop_catalogue.json` (12 books),
`weather_readings.csv` (8,784 hourly rows,
leap year 2024), `mixed_dates.csv` (8 rows,
four date formats, one word in a numeric
column), and `broken.csv` (5 rows, one short
a field, one with an unclosed quote). The
specimens are named in
`examples/lab-notes.txt`. One build
correction, for the record: the first builder
draft wrote the CSVs with CRLF line endings
(Python `csv`'s default), and a mixed-ending
file later defeated the sniffer when a row
was appended in a capture; the builder was
fixed to write LF and the byte-dependent
captures (06, 23–25, 52) were retaken.

**Verified by running, per chapter:**

- *Ch. 1:* `duckdb --version` (1.4.1 Andium);
  the lab build itself, with its five counts
  (120 / 12 / 8,784 / 8 / 5).
- *Ch. 2:* the in-place count over the sales
  CSV (120); the first five rows with their
  inferred types; `DESCRIBE` of the sales CSV
  (BIGINT / DATE / BIGINT / VARCHAR / BIGINT
  / DOUBLE / BIGINT) and of the JSON
  catalogue; `SUMMARIZE` over the sales file
  (kept whole in the transcripts; quoted
  selectively in the chapter because the
  table is twelve statistics wide); the
  `FROM`-first form (tills 40 / 40 / 40); and
  the no-import proof — a row appended to a
  copy of the sales file, next count 121.
- *Ch. 3:* the sniffer keeping `shelf_code`
  as VARCHAR with its zeros in 1.4.1; the
  same column forced to BIGINT in a full
  `columns={}` map (0029 → 29); a partial
  one-entry map failing with the header
  mismatch error; the takings sum as DOUBLE
  (3711.809999999997) against the DECIMAL
  read (3711.81); `DESCRIBE` of the mixed
  file (all VARCHAR); its text sort, out of
  order as printed; the bare `CAST` to DATE
  failing with its conversion error verbatim;
  the `try_strptime` coalesce rescuing all
  eight rows in true date order; `TRY_CAST`
  of the stock column (seven numbers, one
  NULL for "twelve").
- *Ch. 4:* the CSV⋈JSON join on `book_id`
  (top five titles by takings, 630.00 first);
  the genre table the same join feeds
  (6 genres, 120 sales, 240 copies); and the
  join repeated on `shelf_code` — text on
  both sides — pairing all 120 sales.
- *Ch. 5:* monthly sales (45 / 45 / 30;
  1491.64 / 1258.72 / 961.45, summing to the
  3711.81 of chapter 3); monthly weather
  (744 readings in January, 696 in leap
  February); the per-genre `rank()` window
  with `QUALIFY` (one row per genre); the
  running rain total window (first ten days,
  the daily grouping itself counted at 366
  days, and the year total 5,403.4 mm from
  the aggregate capture).
- *Ch. 6:* `COPY TO` CSV (76 bytes for the
  genre summary) and JSON with `(ARRAY
  true)`; the whole weather file to Parquet
  (275,981 bytes of CSV → 83,073 bytes) with
  the row count proven equal (8,784) from
  the Parquet itself; `DESCRIBE` of the
  Parquet (types stored, none guessed); and
  the `.timer` pair, one run each (CSV real
  0.044 s, Parquet real 0.014 s), quoted in
  the chapter with their single-run health
  warning attached.
- *Ch. 7:* creating `lab.duckdb` (536,576
  bytes), a table and a view in it (`SHOW
  TABLES`), reopening it in a later process
  and counting 120; the `:memory:` contrast
  (`Table with name t does not exist!` in the
  second session); the second-writer refusal
  with its lock error and exit 1, the first
  connection held open for the purpose; and
  two simultaneous `-readonly` connections
  each returning 120.
- *Ch. 8:* `.help` in full (52 lines, kept in
  the transcripts, quoted selectively);
  `.mode list` with `.headers off`; `.mode
  json`; `.tables` and `.schema` in-session;
  `.output` diverting a result to a file and
  back to stdout; the `.timer on` line
  format from chapter 6's runs.
- *Ch. 9 (recipes):* recipes 1–5 recombine
  captures verified in their home chapters.
  Recipe 6 was run for real: `pip install
  duckdb==1.4.1` into a fresh venv, and a
  script joining the two shop files and
  totalling the weather file, printing the
  same answers as the CLI (240 copies by
  genre; 5,403.4 mm).
- *Ch. 11:* every error quoted is a capture,
  including the malformed-file trilogy: the
  sniffed read collapsing `broken.csv` to
  one VARCHAR column (`count(*)` still 5);
  the forced-columns read refused at
  sniffing, with DuckDB's own fix list; and
  `ignore_errors=true` returning the three
  good rows typed (1, 3, 5). Between those,
  several knob combinations (`strict_mode`,
  `null_padding`, pinned delimiter/quote)
  were tried and failed at the same sniffing
  stage; their transcripts are kept
  (39, 40, 43, 44) so the record shows the
  attempts, not just the winner.

**Capture hygiene (declared trims):** wide
tables are shown compactly in three places,
and the two read-only result boxes in
chapter 7 are summarised as one line with
their values as captured —
the JSON `DESCRIBE` (chapter 2), the genre
table (chapter 4), and the window winners
(chapter 5) — always with every value as
captured and the full table in the
transcripts. The long CSV sniffing error is
quoted by its decisive lines in chapters 3
and 11, never in full; the whole text is in
transcripts 39–47. The lock error's file path
is shortened with an ellipsis in chapter 7;
the PID is as captured. Timings are single
runs, labelled as such where quoted.

**Build-machine weather, stated once:** the
lab's files sit on an overlay filesystem
that assigns group `nogroup` and, with the
workspace's umask of 007, mode 660. The
`ls -l` lines in chapters 6 and 7 show that
machine's modes and owner-group, not
properties of the files.

**Documented-only (not run), and why:**

- *Installation on Windows and macOS:* the
  tested binary is the Linux amd64 CLI. The
  other platforms' downloads are the same
  program in different archives; the guide
  says "one downloaded binary" and does not
  narrate installs it did not perform.
- *Extensions (httpfs/S3, spatial, Iceberg,
  the `-ui` browser interface):* not
  exercised. The lab is local files on
  purpose, and there is no browser on the
  build machine. The README names the
  ecosystem as out of scope rather than
  describing behaviour from documentation.
- *Other language clients (R, Node, Java,
  Go, …):* not run. The Python client was
  run (recipe 6); the others are placed, not
  taught, in chapter 10's terms.
- *Multi-file and glob reads, hive
  partitioning, ATTACH of a second
  database:* real DuckDB features the guide
  does not teach, so nothing about them is
  quoted or claimed.
- *The neighbours' internals:* chapter 10
  places SQLite, PostgreSQL, jq,
  spreadsheets, and pandas from their
  documented designs; no comparative
  benchmark against any of them was run,
  and none is quoted.

Specimen discipline, for the record: every
shop, book, author, and weather station in
the lab is invented; the weather values are
a seeded random walk, plausible and nobody's
real readings; the only files the chapters
write are exports and database files the
reader is told are disposable, and the one
destructive experiment — the second writer —
was aimed at a database file built for the
purpose. The guide's one self-inflicted
wound, the `?access_mode=` filename, is
confessed in chapter 7 and filed in chapter
11 rather than tidied away.
