📦 E-Commerce Synthetic Data Project (Cursor IDE + SQLite)

This project demonstrates a complete workflow for generating synthetic e-commerce data, ingesting it into a SQLite database, and running SQL join queries to analyze the data.
The project was completed using Cursor IDE, GitHub, Python, Pandas, and SQLite.

**prompts for each section**

**Generate 5 CSV files** for a synthetic e-commerce dataset. Output only the CSV contents, each prefixed by a filename line like "=== customers.csv ===" then the CSV text.

Files & columns:
1) customers.csv: customer_id,int PK; first_name; last_name; email; created_at (YYYY-MM-DD). Rows: 500.
2) categories.csv: category_id,int PK; category_name. Rows: 12.
3) products.csv: product_id,int PK; product_name; category_id (FK); price; sku. Rows: 200.
4) orders.csv: order_id,int PK; customer_id (FK); order_date; total_amount. Rows: 1500.
5) order_items.csv: order_item_id,int PK; order_id; product_id; quantity (int), unit_price (decimal). ~2500 rows.

Constraints:
- Ensure FK consistency.
- Dates within last 2 years.
- Output only CSV blocks with headers.
- 
  **Sqlite Section**
  import sqlite3
import pandas as pd

# Database name
DB_NAME = "ecommerce.db"

def create_tables(conn):
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        created_at TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY,
        category_name TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT,
        category_id INTEGER,
        price REAL,
        sku TEXT,
        FOREIGN KEY(category_id) REFERENCES categories(category_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date TEXT,
        total_amount REAL,
        FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        order_item_id INTEGER PRIMARY KEY,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        unit_price REAL,
        FOREIGN KEY(order_id) REFERENCES orders(order_id),
        FOREIGN KEY(product_id) REFERENCES products(product_id)
    );
    """)

    conn.commit()


def load_csv(conn, file, table):
    df = pd.read_csv(file)
    df.to_sql(table, conn, if_exists="append", index=False)
    print(f"Inserted {len(df)} rows into {table}")


def main():
    conn = sqlite3.connect(DB_NAME)
    create_tables(conn)

    load_csv(conn, "customers.csv", "customers")
    load_csv(conn, "categories.csv", "categories")
    load_csv(conn, "products.csv", "products")
    load_csv(conn, "orders.csv", "orders")
    load_csv(conn, "order_items.csv", "order_items")

    conn.close()
    print("\nDatabase ingestion complete!")


if _name_ == "_main_":
    main()

**Sql Query**
-- query.sql
WITH recent_orders AS (
  SELECT * FROM orders
  WHERE DATE(order_date) >= DATE('now','-12 months')
),
cust_spend AS (
  SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS full_name,
    c.email,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COALESCE(SUM(oi.quantity),0) AS total_items,
    COALESCE(SUM(oi.quantity * oi.unit_price),0) AS total_spent,
    MAX(o.order_date) AS last_order_date
  FROM customers c
  JOIN recent_orders o ON o.customer_id = c.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY c.customer_id
),
cust_category_spend AS (
  SELECT
    c.customer_id,
    cat.category_id,
    cat.category_name,
    SUM(oi.quantity * oi.unit_price) AS cat_spent
  FROM customers c
  JOIN recent_orders o ON o.customer_id = c.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  JOIN categories cat ON cat.category_id = p.category_id
  GROUP BY c.customer_id, cat.category_id
),
favorite_cat AS (
  SELECT customer_id, category_name
  FROM (
    SELECT
      customer_id,
      category_name,
      cat_spent,
      ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY cat_spent DESC) AS rn
    FROM cust_category_spend
  ) t
  WHERE rn = 1
)
SELECT
  cs.customer_id,
  cs.full_name,
  cs.email,
  cs.total_orders,
  cs.total_items,
  ROUND(cs.total_spent,2) AS total_spent,
  cs.last_order_date,
  COALESCE(fc.category_name, 'Unknown') AS favorite_category
FROM cust_spend cs
LEFT JOIN favorite_cat fc ON fc.customer_id = cs.customer_id
ORDER BY cs.total_spent DESC
LIMIT 10;

**python code section***
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
