import duckdb

con = duckdb.connect()  # in-memory, like starting the CLI bare

rows = con.execute("""
    SELECT c.genre, sum(s.qty) AS copies
    FROM 'data/bookshop_sales.csv' AS s
    JOIN 'data/bookshop_catalogue.json' AS c ON s.book_id = c.book_id
    GROUP BY c.genre
    ORDER BY copies DESC
""").fetchall()
for genre, copies in rows:
    print(f"{genre}: {copies}")

rain = con.execute("""
    SELECT round(sum(rain_mm), 1) FROM 'data/weather_readings.csv'
""").fetchone()
print("rain in 2024, mm:", rain[0])
