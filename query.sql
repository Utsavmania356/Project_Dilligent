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