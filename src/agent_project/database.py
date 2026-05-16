"""
SQLite database with e-commerce demo data.
Tables: categories, products, customers, orders, order_items.
"""
import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

from agent_project.config import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_database():
    """Create tables and populate with demo data if not already initialized."""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categories'")
    if cursor.fetchone():
        conn.close()
        return

    # --- Tables ---
    cursor.executescript("""
        CREATE TABLE categories (
            id          INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE products (
            id          INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            category_id INTEGER NOT NULL REFERENCES categories(id),
            price       REAL NOT NULL,
            cost        REAL NOT NULL,
            stock       INTEGER NOT NULL
        );

        CREATE TABLE customers (
            id          INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            city        TEXT NOT NULL,
            level       TEXT NOT NULL DEFAULT '普通',
            created_at  TEXT NOT NULL
        );

        CREATE TABLE orders (
            id          INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL REFERENCES customers(id),
            order_date  TEXT NOT NULL,
            total_amount REAL NOT NULL,
            status      TEXT NOT NULL DEFAULT '已完成'
        );

        CREATE TABLE order_items (
            id          INTEGER PRIMARY KEY,
            order_id    INTEGER NOT NULL REFERENCES orders(id),
            product_id  INTEGER NOT NULL REFERENCES products(id),
            quantity    INTEGER NOT NULL,
            unit_price  REAL NOT NULL,
            subtotal    REAL NOT NULL
        );
    """)

    # --- Demo Data ---
    categories = [
        (1, "数码电子", "手机、电脑、平板等电子产品"),
        (2, "服装鞋帽", "男装、女装、鞋类、帽子等"),
        (3, "食品饮料", "零食、饮料、生鲜等"),
        (4, "家居用品", "家具、厨具、家纺等"),
        (5, "运动户外", "运动装备、户外用品等"),
    ]
    cursor.executemany("INSERT INTO categories VALUES (?, ?, ?)", categories)

    products = [
        (1, "iPhone 15", 1, 5999, 4500, 120),
        (2, "华为 Mate 60", 1, 5499, 4200, 85),
        (3, "MacBook Air", 1, 7999, 6000, 40),
        (4, "小米 14", 1, 3999, 3000, 150),
        (5, "AirPods Pro", 1, 1499, 900, 200),
        (6, "男士羽绒服", 2, 899, 500, 60),
        (7, "女士连衣裙", 2, 399, 200, 180),
        (8, "运动跑鞋", 2, 599, 350, 100),
        (9, "休闲卫衣", 2, 299, 150, 200),
        (10, "三只松鼠坚果礼盒", 3, 128, 70, 500),
        (11, "伊利纯牛奶", 3, 68, 40, 300),
        (12, "农夫山泉矿泉水", 3, 2, 1, 2000),
        (13, "进口咖啡豆", 3, 198, 120, 80),
        (14, "智能台灯", 4, 249, 150, 90),
        (15, "记忆棉枕头", 4, 199, 100, 150),
        (16, "不锈钢锅具三件套", 4, 499, 300, 60),
        (17, "瑜伽垫", 5, 99, 50, 200),
        (18, "登山背包", 5, 399, 220, 70),
        (19, "跑步机", 5, 2999, 2000, 25),
        (20, "羽毛球拍", 5, 199, 110, 130),
    ]
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)", products)

    cities = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京"]
    customers = []
    for i in range(1, 31):
        city = random.choice(cities)
        created = datetime(2024, random.randint(1, 12), random.randint(1, 28))
        level = random.choices(["普通", "银卡", "金卡"], weights=[6, 3, 1])[0]
        customers.append((i, f"客户{i:02d}", city, level, created.strftime("%Y-%m-%d")))
    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?)", customers)

    statuses = ["已完成", "已完成", "已完成", "已发货", "已取消", "退货中"]
    orders = []
    order_items = []
    order_id = 1
    item_id = 1

    for _ in range(200):
        customer_id = random.randint(1, 30)
        days_ago = random.randint(0, 90)
        order_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        status = random.choice(statuses)

        num_items = random.randint(1, 4)
        total = 0
        for _ in range(num_items):
            product = random.choice(products)
            quantity = random.randint(1, 5)
            subtotal = round(product[3] * quantity, 2)
            total += subtotal
            order_items.append((item_id, order_id, product[0], quantity, product[3], subtotal))
            item_id += 1

        orders.append((order_id, customer_id, order_date, round(total, 2), status))
        order_id += 1

    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", orders)
    cursor.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?, ?)", order_items)

    conn.commit()
    conn.close()


SCHEMA_DOC = """
## 数据库表结构

### categories — 产品分类表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 分类名称 |
| description | TEXT | 分类描述 |

### products — 产品表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 产品名称 |
| category_id | INTEGER | 所属分类，关联 categories.id |
| price | REAL | 售价（元） |
| cost | REAL | 成本（元） |
| stock | INTEGER | 库存数量 |

### customers — 客户表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 客户姓名 |
| city | TEXT | 所在城市 |
| level | TEXT | 会员等级：普通/银卡/金卡 |
| created_at | TEXT | 注册日期 YYYY-MM-DD |

### orders — 订单表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| customer_id | INTEGER | 客户ID，关联 customers.id |
| order_date | TEXT | 下单日期 YYYY-MM-DD |
| total_amount | REAL | 订单总金额（元） |
| status | TEXT | 状态：已完成/已发货/已取消/退货中 |

### order_items — 订单明细表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| order_id | INTEGER | 订单ID，关联 orders.id |
| product_id | INTEGER | 产品ID，关联 products.id |
| quantity | INTEGER | 购买数量 |
| unit_price | REAL | 下单时单价（元） |
| subtotal | REAL | 小计（quantity × unit_price） |
"""

QUERY_EXAMPLES = """
示例1: "哪个品类销售额最高？"
SQL: SELECT c.name, SUM(oi.subtotal) as total_sales FROM categories c JOIN products p ON c.id = p.category_id JOIN order_items oi ON p.id = oi.product_id JOIN orders o ON oi.order_id = o.id WHERE o.status = '已完成' GROUP BY c.id, c.name ORDER BY total_sales DESC;

示例2: "上个月卖得最好的5个产品是什么？"
SQL: SELECT p.name, SUM(oi.quantity) as sold FROM products p JOIN order_items oi ON p.id = oi.product_id JOIN orders o ON oi.order_id = o.id WHERE o.order_date >= date('now', '-1 month') AND o.status = '已完成' GROUP BY p.id, p.name ORDER BY sold DESC LIMIT 5;

示例3: "各城市的销售额排名？"
SQL: SELECT c.city, SUM(o.total_amount) as total FROM customers c JOIN orders o ON c.id = o.customer_id WHERE o.status = '已完成' GROUP BY c.city ORDER BY total DESC;

示例4: "金卡会员的平均客单价是多少？"
SQL: SELECT AVG(o.total_amount) FROM orders o JOIN customers c ON o.customer_id = c.id WHERE c.level = '金卡' AND o.status = '已完成';

示例5: "最近7天的销售趋势？"
SQL: SELECT o.order_date, SUM(o.total_amount) as daily_total, COUNT(o.id) as order_count FROM orders o WHERE o.order_date >= date('now', '-7 days') AND o.status = '已完成' GROUP BY o.order_date ORDER BY o.order_date;
"""


if __name__ == "__main__":
    init_database()
    print(f"Database initialized at {DB_PATH}")
