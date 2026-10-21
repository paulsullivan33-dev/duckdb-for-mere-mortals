# When It Guesses Wrong

**Scope:** the sniffer — what it samples, what
it decides, and the three ways its guesses
cost you: codes that lose their zeros, money
that gains a tail of nines, and dates that
were never one format to begin with. Also the
fixing tools: `columns={}`, `CAST`,
`TRY_CAST`, and `try_strptime`.

## Meet the sniffer

Every in-place read in chapter 2 began with a
guess. DuckDB's CSV reader — the **sniffer** —
samples the top of the file (its report,
captured in this chapter's error messages,
admits `sample_size = 20480` rows) and decides
the dialect: the delimiter, the quote
character, whether a header row exists, and a
type for every column. JSON needs less
guessing, Parquet none at all — those formats
carry their answers with them — which is why
this chapter is mostly about CSV.

On the lab's sales file the sniffer scored
full marks, including the subtle one:
`shelf_code` came out `VARCHAR`, so `0029`
stayed `0029`. In version 1.4.1 the sniffer
treats zero-padded numbers as text rather
than lose the zeros. That is a kindness of
this version, not a law of computing, and the
next section shows how thin the ice is.

## Codes are not numbers

A shelf code, a part number, a ZIP code: these
are **labels that happen to be made of
digits**. Nothing about them is a quantity —
nobody averages two shelf codes — and the
moment anything stores one as a number, the
leading zeros are gone, silently and for
good. Watch it happen. `read_csv` accepts a
`columns={}` map that pins types explicitly;
force `shelf_code` to `BIGINT` (the full map
is used here — the next section explains why
it must be full) and read the same rows:

```
$ duckdb -c "SELECT sale_id, shelf_code FROM read_csv('data/bookshop_sales.csv', columns={... 'shelf_code': 'BIGINT' ...}) ORDER BY sale_id LIMIT 5;"
┌─────────┬────────────┐
│ sale_id │ shelf_code │
│  int64  │   int64    │
├─────────┼────────────┤
│       1 │         29 │
│       2 │        107 │
│       3 │        63 │
│       4 │         29 │
│       5 │        107 │
└─────────┴────────────┘
```

`0029` is `29` now. No error, no warning —
the values are simply different values, and
any join or comparison against the catalogue
(which kept `0029` as text) would quietly
fail to match, or worse, match after somebody
casts the other side and destroys those zeros
too. The rule costs nothing to state: **if a
column is a code, it is text.** Pin it
`VARCHAR` when you pin anything, and when a
system hands you codes already stored as
numbers, the zeros are already lost — no
tool can know how many there were.

## The map is the whole schema

The `columns={}` map is not a patch on the
sniffer's schema; it **replaces** it. Name
every column, with its type, or the read
fails — a one-entry map against the
seven-column sales file ends in a long error
whose useful tail is:

```
Header mismatch at position: 0
Expected name: "shelf_code", Actual name: "sale_id,sold_on,..."
The Column names set by the user do not match the ones
found by the sniffer.
```

Here is the full map for the sales file, the
form chapters 3 and 9 use whenever an answer
has to be exactly right:

```
read_csv('data/bookshop_sales.csv', columns={
  'sale_id': 'BIGINT', 'sold_on': 'DATE',
  'book_id': 'BIGINT', 'shelf_code': 'VARCHAR',
  'qty': 'BIGINT', 'unit_price': 'DECIMAL(10,2)',
  'till_no': 'BIGINT'})
```

## Money is not a DOUBLE

Why `DECIMAL(10,2)` for the price? Because the
sniffer chose `DOUBLE` — binary floating
point, the type that famously cannot hold
most decimal fractions exactly. Total the
shop's takings both ways:

```
$ duckdb -c "SELECT sum(qty * unit_price) AS takings FROM 'data/bookshop_sales.csv';"
   3711.809999999997          (double)
$ duckdb -c "SELECT sum(qty * unit_price) AS takings FROM read_csv('data/bookshop_sales.csv', columns={... 'unit_price': 'DECIMAL(10,2)' ...});"
   3711.81                    (decimal(38,2))
```

Same file, same rows, two answers, and only
one of them is the shop's money. `round(x, 2)`
hides the dust on a single printed total; it
does nothing for the comparisons and running
sums that dust accumulates inside.
**Money gets DECIMAL**, whose two numbers are
a budget: `DECIMAL(10,2)` holds ten digits in
all, two of them after the point.

## The file that had four date formats

`mixed_dates.csv` is the cautionary specimen:
eight stock arrivals, four date formats, one
stock column that is a word once. The
sniffer's verdict, from `DESCRIBE`:

```
item        VARCHAR
arrived_on  VARCHAR
stock       VARCHAR
```

No single date format fits `2024-03-01`,
`01/03/2024`, `2024/03/05`, and `March 6,
2024`, so the column stays text — and so does
`stock`, because `twelve` cannot be an
integer and one value decides for all 8 rows.
Text is not a safe fallback; it is a different
wrong answer. Sorted as text, the arrivals
come out in this order — read the dates and
wince:

```
oak stool     01/03/2024
glass jar     07-03-2024
cedar box     11/03/2024
brass lamp    2024-03-01
iron skillet  2024-03-08
enamel mug    2024-03-12
tin kettle    2024/03/05
wool blanket  March 6, 2024
```

`CAST` will not rescue it wholesale either,
because a bare cast assumes ISO format and
stops at the first row that isn't:

```
Conversion Error: invalid date field format: "01/03/2024",
expected format is (YYYY-MM-DD) when casting from
source column arrived_on
```

The rescue is to say the formats yourself.
`try_strptime(value, format)` parses text
against one format string and returns NULL —
not an error — when it doesn't fit, so a
`coalesce` over the candidate formats picks
each row up by the one that matches:

```
SELECT item,
  coalesce(
    try_strptime(arrived_on, '%Y-%m-%d'),
    try_strptime(arrived_on, '%d/%m/%Y'),
    try_strptime(arrived_on, '%Y/%m/%d'),
    try_strptime(arrived_on, '%B %d, %Y'),
    try_strptime(arrived_on, '%d-%m-%Y'))::DATE AS arrived
FROM 'data/mixed_dates.csv' ORDER BY arrived;
```

All eight rows land on true dates, in true
order (capture 11 in the transcripts). And
`TRY_CAST(stock AS INTEGER)` does the same
honest job for the stock column: seven rows
convert, and `twelve` becomes NULL — visible,
countable, nobody's silent zero.

One warning this chapter cannot prove for
you, because no capture can: **`01/03/2024`
is ambiguous.** The lab means it day-first —
1 March — and the rescue above reads it so.
Read it month-first and you get 3 January,
with no error anywhere, on this row and every
row like it. The file does not say which it
means; only whoever produced it knows. When
a date column mixes formats, resolving the
ambiguous ones is a question for a human, and
any tool that answers it without asking is
guessing with your data.

Check: the habits this chapter is selling —

```
1. DESCRIBE every file you didn't write.
2. Codes are VARCHAR. Money is DECIMAL.
3. columns={} names every column, or none.
4. CAST errors are information; TRY_CAST's
   NULLs are a count you should look at.
```
