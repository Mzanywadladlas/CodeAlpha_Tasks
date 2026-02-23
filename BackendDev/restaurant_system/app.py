from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flasgger import Swagger
import sqlite3
from datetime import datetime

app = Flask(__name__)
bcrypt = Bcrypt(app)
swagger = Swagger(app)

DB_NAME = "restaurant.db"

# ---------------------------------------
# Helpers
# ---------------------------------------
def db_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = db_conn()
    c = conn.cursor()

    # USERS
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        );
    """)

    # MENU ITEMS (inventory lives here as 'stock')
    c.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            stock INTEGER
        );
    """)

    # TABLES
    c.execute("""
        CREATE TABLE IF NOT EXISTS tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER UNIQUE,
            capacity INTEGER
        );
    """)

    # RESERVATIONS
    c.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            table_id INTEGER,
            reserved_at TEXT
        );
    """)

    # ORDERS
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            created_at TEXT,
            total REAL
        );
    """)

    # ORDER ITEMS
    c.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            menu_id INTEGER,
            quantity INTEGER,
            price_each REAL,
            subtotal REAL
        );
    """)

    conn.commit()

    # Seed 5 basic tables if none exist
    c.execute("SELECT COUNT(*) FROM tables;")
    count = c.fetchone()[0]
    if count == 0:
        for i in range(1, 6):
            c.execute("INSERT INTO tables(table_number, capacity) VALUES (?, ?)", (i, 4))
        conn.commit()

    conn.close()

init_db()

# ---------------------------------------
# AUTH
# ---------------------------------------
@app.post("/register")
def register():
    """
    Register a new user
    ---
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - in: formData
        name: username
        required: true
      - in: formData
        name: password
        required: true
    responses:
      200:
        description: OK
    """
    username = request.form.get("username", "").strip()
    plain_pw = request.form.get("password", "")

    if not username or not plain_pw:
        return {"error": "username and password required"}, 400

    hashed = bcrypt.generate_password_hash(plain_pw).decode("utf-8")
    try:
        conn = db_conn()
        c = conn.cursor()
        c.execute("INSERT INTO users(username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        return {"message": "User registered!"}
    except sqlite3.IntegrityError:
        return {"error": "Username already exists"}, 400
    finally:
        conn.close()


@app.post("/login")
def login():
    """
    Login (returns user_id on success)
    ---
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - in: formData
        name: username
        required: true
      - in: formData
        name: password
        required: true
    responses:
      200:
        description: OK
    """
    username = request.form.get("username")
    plain_pw = request.form.get("password")

    conn = db_conn()
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()

    if row and bcrypt.check_password_hash(row[1], plain_pw):
        return {"message": "Login successful", "user_id": row[0]}
    return {"error": "Invalid credentials"}, 401

# ---------------------------------------
# MENU (CRUD + Inventory)
# ---------------------------------------
@app.post("/menu")
def create_menu_item():
    """
    Create a menu item
    ---
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - in: formData
        name: name
        required: true
      - in: formData
        name: price
        required: true
        type: number
      - in: formData
        name: stock
        required: true
        type: integer
    responses:
      200:
        description: OK
    """
    name = request.form.get("name")
    price = request.form.get("price", type=float)
    stock = request.form.get("stock", type=int)

    if not name or price is None or stock is None:
        return {"error": "name, price, stock required"}, 400

    conn = db_conn()
    c = conn.cursor()
    c.execute("INSERT INTO menu_items(name, price, stock) VALUES (?,?,?)", (name, price, stock))
    conn.commit()
    item_id = c.lastrowid
    conn.close()
    return {"message": "Menu item created", "id": item_id}


@app.get("/menu")
def list_menu():
    """
    List all menu items (with stock)
    ---
    responses:
      200:
        description: OK
    """
    conn = db_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, price, stock FROM menu_items")
    rows = c.fetchall()
    conn.close()
    items = [{"id": r[0], "name": r[1], "price": r[2], "stock": r[3]} for r in rows]
    return {"menu": items}


@app.get("/menu/<int:menu_id>")
def get_menu_item(menu_id):
    """
    Get a single menu item
    ---
    responses:
      200:
        description: OK
    """
    conn = db_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, price, stock FROM menu_items WHERE id=?", (menu_id,))
    r = c.fetchone()
    conn.close()
    if not r:
        return {"error": "Not found"}, 404
    return {"id": r[0], "name": r[1], "price": r[2], "stock": r[3]}


@app.put("/menu/<int:menu_id>")
def update_menu_item(menu_id):
    """
    Update a menu item (send any of name/price/stock)
    ---
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - in: path
        name: menu_id
        required: true
      - in: formData
        name: name
        required: false
      - in: formData
        name: price
        type: number
        required: false
      - in: formData
        name: stock
        type: integer
        required: false
    """
    name = request.form.get("name")
    price = request.form.get("price", type=float)
    stock = request.form.get("stock", type=int)

    conn = db_conn()
    c = conn.cursor()

    # Read current
    c.execute("SELECT name, price, stock FROM menu_items WHERE id=?", (menu_id,))
    r = c.fetchone()
    if not r:
        conn.close()
        return {"error": "Not found"}, 404

    new_name = name if name is not None else r[0]
    new_price = price if price is not None else r[1]
    new_stock = stock if stock is not None else r[2]

    c.execute("UPDATE menu_items SET name=?, price=?, stock=? WHERE id=?",
              (new_name, new_price, new_stock, menu_id))
    conn.commit()
    conn.close()
    return {"message": "Updated"}

# ---------------------------------------
# TABLES
# ---------------------------------------
@app.post("/tables")
def create_table():
    """
    Create a table (optional; we seed 5 by default)
    ---
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - in: formData
        name: table_number
        type: integer
        required: true
      - in: formData
        name: capacity
        type: integer
        required: true
    """
    table_number = request.form.get("table_number", type=int)
    capacity = request.form.get("capacity", type=int)
    if table_number is None or capacity is None:
        return {"error": "table_number and capacity required"}, 400

    try:
        conn = db_conn()
        c = conn.cursor()
        c.execute("INSERT INTO tables(table_number, capacity) VALUES (?,?)",
                  (table_number, capacity))
        conn.commit()
        return {"message": "Table created"}
    except sqlite3.IntegrityError:
        return {"error": "table_number already exists"}, 400
    finally:
        conn.close()


@app.get("/tables")
def list_tables():
    """
    List all tables
    ---
    responses:
      200:
        description: OK
    """
    conn = db_conn()
    c = conn.cursor()
    c.execute("SELECT id, table_number, capacity FROM tables")
    rows = c.fetchall()
    conn.close()
    return {
        "tables": [{"id": r[0], "table_number": r[1], "capacity": r[2]} for r in rows]
    }

# ---------------------------------------
# RESERVATIONS
# ---------------------------------------
@app.post("/reserve")
def reserve_table():
    """
    Reserve a table (simple conflict check)
    ---
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - in: formData
        name: user_id
        type: integer
        required: true
      - in: formData
        name: table_id
        type: integer
        required: true
      - in: formData
        name: reserved_at
        required: true
        description: "Use 'YYYY-MM-DD HH:MM' (e.g., 2026-02-20 19:30)"
    responses:
      200:
        description: OK
    """
    user_id = request.form.get("user_id", type=int)
    table_id = request.form.get("table_id", type=int)
    reserved_at = request.form.get("reserved_at")

    if not (user_id and table_id and reserved_at):
        return {"error": "user_id, table_id, reserved_at required"}, 400

    # Optional: validate datetime format
    try:
        datetime.strptime(reserved_at, "%Y-%m-%d %H:%M")
    except ValueError:
        return {"error": "reserved_at must be 'YYYY-MM-DD HH:MM'"}, 400

    conn = db_conn()
    c = conn.cursor()

    # conflict check: same table+time slot
    c.execute("""
        SELECT id FROM reservations
        WHERE table_id=? AND reserved_at=?
    """, (table_id, reserved_at))
    if c.fetchone():
        conn.close()
        return {"error": "Table already reserved for that time"}, 409

    c.execute("INSERT INTO reservations(user_id, table_id, reserved_at) VALUES (?,?,?)",
              (user_id, table_id, reserved_at))
    conn.commit()
    res_id = c.lastrowid
    conn.close()
    return {"message": "Reservation confirmed", "reservation_id": res_id}


@app.post("/cancel_reservation")
def cancel_reservation():
    """
    Cancel a reservation (must belong to the user)
    ---
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - in: formData
        name: user_id
        type: integer
        required: true
      - in: formData
        name: reservation_id
        type: integer
        required: true
    """
    user_id = request.form.get("user_id", type=int)
    reservation_id = request.form.get("reservation_id", type=int)

    conn = db_conn()
    c = conn.cursor()
    c.execute("DELETE FROM reservations WHERE id=? AND user_id=?", (reservation_id, user_id))
    conn.commit()
    deleted = c.rowcount
    conn.close()

    if deleted == 0:
        return {"error": "Not found or not your reservation"}, 404
    return {"message": "Reservation cancelled"}


@app.get("/my_reservations/<int:user_id>")
def my_reservations(user_id):
    """
    List the user's reservations
    ---
    responses:
      200:
        description: OK
    """
    conn = db_conn()
    c = conn.cursor()
    c.execute("""
        SELECT r.id, r.reserved_at, t.table_number, t.capacity
        FROM reservations r
        JOIN tables t ON r.table_id = t.id
        WHERE r.user_id=?
        ORDER BY r.reserved_at
    """, (user_id,))
    rows = c.fetchall()
    conn.close()
    return {
        "reservations": [
            {"reservation_id": r[0], "reserved_at": r[1],
             "table_number": r[2], "capacity": r[3]}
            for r in rows
        ]
    }

# ---------------------------------------
# ORDERS (with inventory update)
# ---------------------------------------
@app.post("/orders")
def create_order():
    """
    Create an order (JSON body). Automatically reduces stock.
    ---
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: integer
            items:
              type: array
              items:
                type: object
                properties:
                  menu_id:
                    type: integer
                  qty:
                    type: integer
          example:
            user_id: 1
            items:
              - { "menu_id": 1, "qty": 2 }
              - { "menu_id": 3, "qty": 1 }
    responses:
      200:
        description: Order created
    """
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    items = data.get("items", [])

    if not user_id or not items:
        return {"error": "user_id and items[] required"}, 400

    conn = db_conn()
    c = conn.cursor()

    # Validate stock for all items first
    for it in items:
        menu_id = it.get("menu_id")
        qty = it.get("qty", 0)
        if not (menu_id and qty > 0):
            conn.close()
            return {"error": "Each item needs menu_id and qty>0"}, 400

        c.execute("SELECT name, price, stock FROM menu_items WHERE id=?", (menu_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            return {"error": f"Menu item {menu_id} not found"}, 404
        if row[2] < qty:
            conn.close()
            return {"error": f"Not enough stock for '{row[0]}' (have {row[2]}, need {qty})"}, 409

    # Create order
    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO orders(user_id, created_at, total) VALUES (?,?,?)", (user_id, created_at, 0.0))
    order_id = c.lastrowid
    order_total = 0.0

    # Insert order_items and reduce stock
    for it in items:
        menu_id = it["menu_id"]
        qty = int(it["qty"])

        c.execute("SELECT price, stock FROM menu_items WHERE id=?", (menu_id,))
        price, stock = c.fetchone()
        subtotal = price * qty
        order_total += subtotal

        c.execute("""INSERT INTO order_items(order_id, menu_id, quantity, price_each, subtotal)
                     VALUES (?,?,?,?,?)""", (order_id, menu_id, qty, price, subtotal))

        c.execute("UPDATE menu_items SET stock=? WHERE id=?", (stock - qty, menu_id))

    # Update total
    c.execute("UPDATE orders SET total=? WHERE id=?", (order_total, order_id))
    conn.commit()
    conn.close()

    return {"message": "Order created", "order_id": order_id, "total": order_total}


@app.get("/orders/<int:user_id>")
def list_orders(user_id):
    """
    List orders for a user (with items)
    ---
    responses:
      200:
        description: OK
    """
    conn = db_conn()
    c = conn.cursor()

    # Orders
    c.execute("SELECT id, created_at, total FROM orders WHERE user_id=? ORDER BY id DESC", (user_id,))
    orders = c.fetchall()

    result = []
    for o in orders:
        order_id, created_at, total = o
        c.execute("""
            SELECT m.name, oi.quantity, oi.price_each, oi.subtotal
            FROM order_items oi
            JOIN menu_items m ON oi.menu_id = m.id
            WHERE oi.order_id=?
        """, (order_id,))
        items = [{"name": r[0], "qty": r[1], "price_each": r[2], "subtotal": r[3]} for r in c.fetchall()]
        result.append({"order_id": order_id, "created_at": created_at, "total": total, "items": items})

    conn.close()
    return {"orders": result}

# Convenience endpoint to view inventory
@app.get("/inventory")
def inventory():
    """
    Current inventory (stock per menu item)
    ---
    responses:
      200:
        description: OK
    """
    conn = db_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, stock FROM menu_items ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return {"inventory": [{"id": r[0], "name": r[1], "stock": r[2]} for r in rows]}

# ---------------------------------------
# Run
# ---------------------------------------
if __name__ == "__main__":
    app.run(debug=True)