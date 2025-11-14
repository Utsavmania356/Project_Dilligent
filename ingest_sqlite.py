import sqlite3
import sys

# defensive import for pandas with a helpful error message
try:
    import pandas as pd
except ModuleNotFoundError:
    print(
        "ERROR: pandas is not installed in this Python environment.\n"
        "Install it with: python -m pip install pandas\n"
        "Then re-run this script with the same `python` command you used to install pandas."
    )
    sys.exit(1)

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
    try:
        df = pd.read_csv(file)
    except FileNotFoundError:
        print(f"Warning: {file} not found — skipping {table}.")
        return
    except pd.errors.EmptyDataError:
        print(f"Warning: {file} is empty — skipping {table}.")
        return
    except Exception as e:
        print(f"Error reading {file}: {e}")
        return

    # If table doesn't exist or columns mismatch, pandas will attempt to create or append accordingly.
    try:
        df.to_sql(table, conn, if_exists="append", index=False)
        print(f"Inserted {len(df)} rows into {table}")
    except ValueError as e:
        print(f"Error inserting into {table}: {e}")
    except Exception as e:
        print(f"Unexpected error while inserting into {table}: {e}")


def main():
    conn = sqlite3.connect(DB_NAME)
    try:
        create_tables(conn)

        load_csv(conn, "customers.csv", "customers")
        load_csv(conn, "categories.csv", "categories")
        load_csv(conn, "products.csv", "products")
        load_csv(conn, "orders.csv", "orders")
        load_csv(conn, "order_items.csv", "order_items")

    finally:
        conn.close()

    print("\nDatabase ingestion complete!")


if __name__ == "__main__":
    main()
