from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import sqlite3
from pathlib import Path
from datetime import datetime
 
app = Flask(__name__)
api = Api(app)
 
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "restaurant.db"
 
# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
 
def init_db():
    with get_db() as conn:
        # MENU TABLE
        conn.execute("""
        CREATE TABLE IF NOT EXISTS menu(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
        """)
 
        # TABLES
        conn.execute("""
        CREATE TABLE IF NOT EXISTS tables(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER UNIQUE,
            seats INTEGER,
            is_reserved INTEGER DEFAULT 0
        )
        """)
 
        # ORDERS
        conn.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            quantity INTEGER,
            total_price REAL,
            created_at TEXT
        )
        """)
 
# ================= VALIDATION =================
def checkPostedData(postedData, functionName):
 
    if functionName == "add_menu":
        if "name" not in postedData or "price" not in postedData or "stock" not in postedData:
            return 301
        else:
            return 200
 
    elif functionName == "place_order":
        if "item_id" not in postedData or "quantity" not in postedData:
            return 301
        elif int(postedData["quantity"]) <= 0:
            return 302
        else:
            return 200
 
    elif functionName == "reserve_table":
        if "table_number" not in postedData:
            return 301
        else:
            return 200
 
    return 200
 
# ================= MENU RESOURCES =================
class AddMenuItem(Resource):
    def post(self):
        postedData = request.get_json()
 
        status_code = checkPostedData(postedData, "add_menu")
        if status_code != 200:
            return jsonify({
                "Message": "Missing menu parameters",
                "Status Code": status_code
            })
 
        name = postedData["name"]
        price = float(postedData["price"])
        stock = int(postedData["stock"])
 
        with get_db() as conn:
            conn.execute(
                "INSERT INTO menu(name, price, stock) VALUES(?,?,?)",
                (name, price, stock)
            )
 
        return jsonify({
            "Message": "Menu item added",
            "Status Code": 200
        })
 
class ViewMenu(Resource):
    def get(self):
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM menu").fetchall()
 
        menu = [dict(r) for r in rows]
 
        return jsonify({
            "Message": menu,
            "Status Code": 200
        })
 
# ================= ORDER RESOURCES =================
class PlaceOrder(Resource):
    def post(self):
        postedData = request.get_json()
 
        status_code = checkPostedData(postedData, "place_order")
        if status_code != 200:
            return jsonify({
                "Message": "Invalid order data",
                "Status Code": status_code
            })
 
        item_id = int(postedData["item_id"])
        quantity = int(postedData["quantity"])
 
        with get_db() as conn:
            item = conn.execute(
                "SELECT * FROM menu WHERE id=?",
                (item_id,)
            ).fetchone()
 
            if not item:
                return jsonify({
                    "Message": "Menu item not found",
                    "Status Code": 404
                })
 
            if item["stock"] < quantity:
                return jsonify({
                    "Message": "Insufficient stock",
                    "Status Code": 303
                })
 
            total_price = item["price"] * quantity
            now = datetime.utcnow().isoformat()
 
            # Deduct inventory automatically
            new_stock = item["stock"] - quantity
            conn.execute(
                "UPDATE menu SET stock=? WHERE id=?",
                (new_stock, item_id)
            )
 
            conn.execute("""
            INSERT INTO orders(item_id, quantity, total_price, created_at)
            VALUES(?,?,?,?)
            """, (item_id, quantity, total_price, now))
 
        return jsonify({
            "Message": "Order placed successfully",
            "Total Price": total_price,
            "Status Code": 200
        })
 
class ViewOrders(Resource):
    def get(self):
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM orders").fetchall()
 
        orders = [dict(r) for r in rows]
 
        return jsonify({
            "Message": orders,
            "Status Code": 200
        })
 
# ================= TABLE RESOURCES =================
class AddTable(Resource):
    def post(self):
        postedData = request.get_json()
 
        if "table_number" not in postedData or "seats" not in postedData:
            return jsonify({
                "Message": "Missing table data",
                "Status Code": 301
            })
 
        table_number = int(postedData["table_number"])
        seats = int(postedData["seats"])
 
        with get_db() as conn:
            conn.execute(
                "INSERT INTO tables(table_number, seats) VALUES(?,?)",
                (table_number, seats)
            )
 
        return jsonify({
            "Message": "Table added",
            "Status Code": 200
        })
 
class ReserveTable(Resource):
    def post(self):
        postedData = request.get_json()
 
        status_code = checkPostedData(postedData, "reserve_table")
        if status_code != 200:
            return jsonify({
                "Message": "Missing table number",
                "Status Code": status_code
            })
 
        table_number = int(postedData["table_number"])
 
        with get_db() as conn:
            table = conn.execute(
                "SELECT * FROM tables WHERE table_number=?",
                (table_number,)
            ).fetchone()
 
            if not table:
                return jsonify({
                    "Message": "Table not found",
                    "Status Code": 404
                })
 
            if table["is_reserved"] == 1:
                return jsonify({
                    "Message": "Table already reserved",
                    "Status Code": 302
                })
 
            conn.execute(
                "UPDATE tables SET is_reserved=1 WHERE table_number=?",
                (table_number,)
            )
 
        return jsonify({
            "Message": "Table reserved successfully",
            "Status Code": 200
        })
 
class ViewTables(Resource):
    def get(self):
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM tables").fetchall()
 
        tables = [dict(r) for r in rows]
 
        return jsonify({
            "Message": tables,
            "Status Code": 200
        })
 
# ================= ROUTES =================
api.add_resource(AddMenuItem, "/add_menu")  #POST - http://127.0.0.1:5003/add_menu
api.add_resource(ViewMenu, "/menu") #GET - http://127.0.0.1:5003/menu
 
api.add_resource(PlaceOrder, "/place_order") #POST - http://127.0.0.1:5003/place_order
api.add_resource(ViewOrders, "/orders") #GET - http://127.0.0.1:5003/orders
 
api.add_resource(AddTable, "/add_table") #POST - http://127.0.0.1:5003/add_table
api.add_resource(ReserveTable, "/reserve_table") #POST - http://127.0.0.1:5003/reserve_table
api.add_resource(ViewTables, "/tables") #GET - http://127.0.0.1:5003/tables
 
@app.route('/')
def home():
    return "Restaurant Management API Running"
 
if __name__ == "__main__":
    init_db()
    app.run(port=5003, debug=True)
