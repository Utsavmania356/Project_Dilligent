import csv
import io
import random
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

random.seed(42)
today = date.today()
start_date = today - timedelta(days=730)

def random_date():
    delta_days = (today - start_date).days
    return (start_date + timedelta(days=random.randint(0, delta_days))).isoformat()

first_names = [
    "Olivia", "Emma", "Noah", "Liam", "Sophia", "Ava", "Isabella", "Mia", "Lucas", "Amelia",
    "Ethan", "Harper", "Elijah", "Charlotte", "Mason", "Evelyn", "Logan", "Abigail", "James", "Luna",
    "Benjamin", "Chloe", "Henry", "Ella", "Alexander", "Grace", "Sebastian", "Hazel", "Jack", "Scarlett"
]

last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"
]

category_names = [
    "Electronics", "Home & Kitchen", "Sports & Outdoors", "Health & Beauty",
    "Toys & Games", "Books", "Clothing", "Pet Supplies", "Automotive",
    "Garden & Patio", "Office Supplies", "Groceries"
]

product_adjectives = [
    "Premium", "Classic", "Modern", "Eco", "Smart", "Ultra", "Compact", "Wireless",
    "Durable", "Vintage", "Deluxe", "Essential", "Portable", "Signature", "Heritage"
]

product_items = [
    "Headphones", "Speaker", "Blender", "Backpack", "Yoga Mat", "Water Bottle", "Coffee Maker",
    "Desk Lamp", "Notebook", "Camera", "Air Purifier", "Cookware Set", "Gaming Mouse", "Sneakers",
    "Jacket", "Sunglasses", "Wireless Charger", "Drill Kit", "Garden Hose", "Pet Bed"
]

customers = []
for cid in range(1, 501):
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = f"{first}.{last}{random.randint(1, 9999)}@example.com".lower()
    created_at = random_date()
    customers.append((cid, first, last, email, created_at))

categories = [(idx + 1, name) for idx, name in enumerate(category_names)]

products = []
product_prices = {}
for pid in range(1, 201):
    name = f"{random.choice(product_adjectives)} {random.choice(product_items)}"
    category_id = random.randint(1, len(categories))
    price = Decimal(random.randint(500, 50000)) / Decimal(100)
    price = price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    sku = f"SKU{pid:05d}"
    products.append((pid, name, category_id, f"{price:.2f}", sku))
    product_prices[pid] = price

orders = []
order_items = []
order_item_id = 1
item_count_choices = [1, 2, 3, 4]
item_count_weights = [50, 35, 12, 3]

for oid in range(1, 1501):
    customer_id = random.randint(1, len(customers))
    order_date = random_date()
    num_items = random.choices(item_count_choices, weights=item_count_weights, k=1)[0]
    order_total = Decimal("0.00")

    for _ in range(num_items):
        product_id = random.randint(1, len(products))
        quantity = random.randint(1, 5)
        base_price = product_prices[product_id]
        multiplier = Decimal(str(random.uniform(0.90, 1.05)))
        unit_price = (base_price * multiplier).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        line_total = unit_price * quantity
        order_total += line_total
        order_items.append((order_item_id, oid, product_id, quantity, f"{unit_price:.2f}"))
        order_item_id += 1

    orders.append((oid, customer_id, order_date, f"{order_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):.2f}"))


def emit_csv(name, headers, rows):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    writer.writerows(rows)
    print(f"=== {name} ===")
    print(buffer.getvalue().strip())

emit_csv(
    "customers.csv",
    ["customer_id", "first_name", "last_name", "email", "created_at"],
    customers,
)
print()
emit_csv(
    "categories.csv",
    ["category_id", "category_name"],
    categories,
)
print()
emit_csv(
    "products.csv",
    ["product_id", "product_name", "category_id", "price", "sku"],
    products,
)
print()
emit_csv(
    "orders.csv",
    ["order_id", "customer_id", "order_date", "total_amount"],
    orders,
)
print()
emit_csv(
    "order_items.csv",
    ["order_item_id", "order_id", "product_id", "quantity", "unit_price"],
    order_items,
)
