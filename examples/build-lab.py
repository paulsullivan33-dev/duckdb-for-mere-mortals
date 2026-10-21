#!/usr/bin/env python3
"""build-lab.py — build the specimen data for
"DuckDB for Mere Mortals".

Usage:  python3 build-lab.py [directory]
Default directory: ./data next to this script.

Every file is deterministic: the same rows, the
same counts, the same bytes on every rebuild.
The specimens are:

  bookshop_sales.csv      120 sales from an
                          invented bookshop,
                          Jan-Mar 2024. Its
                          shelf_code column is
                          written with leading
                          zeros (0007, 0042)
                          on purpose: chapter 3
                          springs the inference
                          trap on it.
  bookshop_catalogue.json the shop's 12 books
                          as a JSON array; the
                          join partner for the
                          sales file in chapter 4.
  weather_readings.csv    8,784 hourly readings
                          (leap year 2024) from
                          one invented weather
                          station: read_at,
                          temp_c, humidity_pct,
                          rain_mm.
  mixed_dates.csv         8 rows whose date
                          column arrives in four
                          different formats,
                          with a stock column
                          that mixes numbers
                          and a word. Chapter 3
                          reads the wreckage.
  broken.csv              5 rows, one short a
                          field and one with an
                          unclosed quote, for
                          the error captures in
                          chapters 3 and 11.

Running it again deletes and recreates the
data directory's contents from scratch. It
only ever touches the one directory named on
its command line, and it refuses to replace a
directory that does not carry its marker.
"""

import csv
import json
import os
import random
import sys
from datetime import date, datetime, timedelta

MARKER_TEXT = "duckdb-for-mere-mortals:v1"

BOOKS = [
    # book_id, title, author, genre, list_price, shelf_code
    (1, "The Clockwork Orchard", "Imogen Hart", "Fiction", 12.99, "0007"),
    (2, "A Field Guide to Clouds", "Tomas Reyes", "Science", 18.50, "0013"),
    (3, "The Salt Road Atlas", "Priya Nair", "Travel", 14.25, "0021"),
    (4, "Knots and Their Uses", "Walter Byrne", "Craft", 9.99, "0029"),
    (5, "The Night Ferry", "Imogen Hart", "Fiction", 11.50, "0034"),
    (6, "Volcanoes of the North", "Tomas Reyes", "Science", 21.00, "0042"),
    (7, "Bread for Beginners", "Mabel Okafor", "Cookery", 16.75, "0058"),
    (8, "The Glass Observatory", "Elias Venn", "Fiction", 13.99, "0063"),
    (9, "Walking the Old Roads", "Priya Nair", "Travel", 12.50, "0071"),
    (10, "A History of Maps", "Clara Whitlock", "History", 19.95, "0088"),
    (11, "The Winter Apiary", "Mabel Okafor", "Cookery", 15.25, "0094"),
    (12, "Empires of Salt", "Clara Whitlock", "History", 17.40, "0107"),
]


def build_sales(path):
    """120 individual sales, Jan 2 - Mar 29 2024."""
    first = date(2024, 1, 2)
    rows = []
    for i in range(120):
        book = BOOKS[(i * 7 + 3) % 12]
        day = first + timedelta(days=(i * 11) % 88)
        qty = (i % 3) + 1
        price = book[4]
        if i % 17 == 0:  # an occasional discount
            price = round(price * 0.9, 2)
        rows.append([i + 1, day.isoformat(), book[0], book[5],
                     qty, f"{price:.2f}", (i % 3) + 1])
    rows.sort(key=lambda r: (r[1], r[0]))
    for n, row in enumerate(rows, 1):
        row[0] = n
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["sale_id", "sold_on", "book_id", "shelf_code",
                    "qty", "unit_price", "till_no"])
        w.writerows(rows)
    return len(rows)


def build_catalogue(path):
    books = [{
        "book_id": b[0], "title": b[1], "author": b[2],
        "genre": b[3], "list_price": b[4], "shelf_code": b[5],
    } for b in BOOKS]
    with open(path, "w") as f:
        json.dump(books, f, indent=2)
        f.write("\n")
    return len(books)


def build_weather(path):
    """Hourly readings for 2024: a seeded random
    walk, plausible rather than real."""
    rng = random.Random(20240229)
    start = datetime(2024, 1, 1, 0, 0)
    rows = []
    temp = 6.0
    for h in range(8784):
        when = start + timedelta(hours=h)
        seasonal = 7.5 - 6.5 * _cos_frac(when.timetuple().tm_yday / 366.0)
        daily = 2.2 * _sin_frac((when.hour - 9) / 24.0)
        temp += rng.uniform(-0.9, 0.9)
        temp = max(-6.0, min(31.0, temp * 0.92 + (seasonal + daily) * 0.08))
        rain = 0.0
        if rng.random() < 0.16:
            rain = round(rng.uniform(0.2, 7.5), 1)
        humidity = int(max(28, min(100, 78 - (temp - seasonal) * 3
                                   + rng.uniform(-9, 9))))
        rows.append([when.strftime("%Y-%m-%d %H:%M:%S"),
                     f"{temp:.1f}", humidity, f"{rain:.1f}"])
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["read_at", "temp_c", "humidity_pct", "rain_mm"])
        w.writerows(rows)
    return len(rows)


def _sin_frac(x):
    import math
    return math.sin(2 * math.pi * x)


def _cos_frac(x):
    import math
    return math.cos(2 * math.pi * x)


def build_mixed(path):
    rows = [
        ["item", "arrived_on", "stock"],
        ["brass lamp", "2024-03-01", "12"],
        ["oak stool", "01/03/2024", "7"],
        ["tin kettle", "2024/03/05", "4"],
        ["wool blanket", "March 6, 2024", "9"],
        ["glass jar", "07-03-2024", "15"],
        ["iron skillet", "2024-03-08", "2"],
        ["cedar box", "11/03/2024", "6"],
        ["enamel mug", "2024-03-12", "twelve"],
    ]
    with open(path, "w", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(rows)
    return len(rows) - 1


def build_broken(path):
    lines = [
        "sale_id,sold_on,book_id,qty",
        "1,2024-01-02,3,2",
        "2,2024-01-02,7",
        "3,2024-01-03,5,1",
        '4,"2024-01-03,9,3',
        "5,2024-01-04,1,1",
    ]
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return len(lines) - 1


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data")
    marker = target.rstrip("/") + ".mere-mortals-fixture"
    if os.path.exists(target):
        if not (os.path.isfile(marker)
                and open(marker).read().strip() == MARKER_TEXT):
            print(f"refusing fixture target: existing unowned "
                  f"directory {target}", file=sys.stderr)
            return 1
        for name in os.listdir(target):
            os.remove(os.path.join(target, name))
    else:
        os.makedirs(target)
    if os.path.exists(marker):
        os.remove(marker)

    counts = {
        "bookshop_sales.csv": build_sales(
            os.path.join(target, "bookshop_sales.csv")),
        "bookshop_catalogue.json": build_catalogue(
            os.path.join(target, "bookshop_catalogue.json")),
        "weather_readings.csv": build_weather(
            os.path.join(target, "weather_readings.csv")),
        "mixed_dates.csv": build_mixed(
            os.path.join(target, "mixed_dates.csv")),
        "broken.csv": build_broken(
            os.path.join(target, "broken.csv")),
    }
    with open(marker, "w") as f:
        f.write(MARKER_TEXT + "\n")
    for name, n in counts.items():
        print(f"{name}: {n} rows")
    print(f"built {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
