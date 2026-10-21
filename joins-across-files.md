# Joins Across Files

**Scope:** one question answered from two
files at once — the bookshop's sales CSV
against its catalogue JSON — and what a join
actually is underneath the syntax.

## The files never merge

Nothing so far has needed the sales and the
catalogue in the same thought. The sales file
knows what sold, when, and for how much; it
has never heard the books' titles. The
catalogue knows titles, authors, and genres;
it has never seen a sale. "Which titles took
the most money?" is a question neither file
can answer alone.

A **join** answers it for the length of one
query. On the way through, DuckDB pairs each
sales row with the catalogue row whose
`book_id` matches — `ON s.book_id = c.book_id`
— and the pair can be selected from as if it
were one wide row. The files are not merged,
copied, or altered; the pairing evaporates
when the query ends:

```
$ duckdb -c "SELECT c.title, sum(s.qty) AS copies, round(sum(s.qty * s.unit_price), 2) AS takings FROM 'data/bookshop_sales.csv' s JOIN 'data/bookshop_catalogue.json' c ON s.book_id = c.book_id GROUP BY c.title ORDER BY takings DESC LIMIT 5;"
┌─────────────────────────┬────────┬─────────┐
│          title          │ copies │ takings │
│         varchar         │ int128 │ double  │
├─────────────────────────┼────────┼─────────┤
│ Volcanoes of the North  │     30 │   630.0 │
│ Empires of Salt         │     30 │  516.78 │
│ The Salt Road Atlas     │     30 │  423.24 │
│ Walking the Old Roads   │     30 │  371.25 │
│ A Field Guide to Clouds │     20 │  366.3 │
└─────────────────────────┴────────┴─────────┘
```

Two formats — a CSV and a JSON document —
joined as if format were a rumour. That is
the analytical shape of chapter 1 made
concrete: the engine cares about rows and
columns, and the containers are just where
the rows happened to be living.

Note the `round(…, 2)` doing cosmetic duty on
a `DOUBLE` sum. Chapter 3 showed the honest
alternative — pin `unit_price` to `DECIMAL`
in the reader — and a real takings report
should do exactly that. Cosmetic rounding in
a chapter about joins is a deliberate
shortcut, labelled as one.

## The aliases are load-bearing

`s` and `c` are not decoration. With two
sources in one query, a bare `book_id` is
ambiguous — both files have one — so each
source gets a short alias and every column
reference says which file it means:
`s.qty` is the sales file's quantity,
`c.genre` the catalogue's genre. Write the
aliases the moment a second source appears,
even when the query would work without them;
the query you extend next week is the one
that breaks.

## Keys have to agree

A join matches on **equality of the key
columns**, and equality is type-strict in the
ways chapter 3 made vivid. The catalogue's
`shelf_code` and the sales file's `shelf_code`
both survived as `VARCHAR` — `0029` equals
`0029` — so the same join would work on
shelf codes. Had either side been stored as
a number, `29` would not equal `0029`, the
join would not error, and it would not match:
rows would simply be missing from the answer,
which is the worst failure shape SQL has.
Before trusting a join, check the keys on
both sides with `DESCRIBE`, and count what
came out against what went in. A join that
silently drops rows is indistinguishable
from a quiet week at the shop until somebody
checks.

The same discipline catches the opposite
accident: a key that matches *too much*.
If the catalogue listed a book twice, every
sale of it would be counted twice, because
each sales row pairs with each matching
catalogue row. Joins multiply before they
answer. `count(*)` before and after — it is
always count before and after.

## One question, grouped

The join also feeds chapter 5's machinery
directly. Totalled per genre instead of per
title, the same pairing produces the shop's
whole quarter in six rows:

```
Science   20 sales   50 copies   996.30
Travel    20 sales   60 copies   794.49
History   20 sales   40 copies   714.28
Fiction   30 sales   50 copies   638.40
Cookery   20 sales   30 copies   469.44
Craft     10 sales   10 copies    98.90
```

(capture 16, shown compactly). `GROUP BY` is
doing the grouping; the join merely widened
the rows it groups. That is the whole pattern
of analytical SQL in one sentence, and the
next chapter pulls the two halves apart to
look at each.
