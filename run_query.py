# run_query.py
import sqlite3
import pandas as pd

conn = sqlite3.connect("ecommerce.db")
sql = open("query.sql", "r").read()
df = pd.read_sql_query(sql, conn)
if df.empty:
    print("No results — consider widening the date window in query.sql.")
else:
    print(df.to_string(index=False))
conn.close()