from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import sqlite3
from pathlib import Path
from datetime import datetime
 
app = Flask(__name__)
api = Api(app)
 
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "events.db"
 
# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
 
def init_db():
    with get_db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS events(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            event_date TEXT
        )
        """)
 
        conn.execute("""
        CREATE TABLE IF NOT EXISTS registrations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            event_id INTEGER
        )
        """)
 
# ================= VALIDATION =================
def checkPostedData(postedData, functionName):
    if functionName == "create_event":
        if "title" not in postedData or "event_date" not in postedData:
            return 301
        else:
            return 200
 
    if functionName == "register":
        if "name" not in postedData or "email" not in postedData or "event_id" not in postedData:
            return 301
        else:
            return 200
 
# ================= RESOURCES =================
class CreateEvent(Resource):
    def post(self):
        postedData = request.get_json()
 
        status_code = checkPostedData(postedData, "create_event")
        if status_code != 200:
            return jsonify({
                "Message": "Missing event fields",
                "Status Code": status_code
            })
 
        title = postedData["title"]
        description = postedData.get("description", "")
        event_date = postedData["event_date"]
 
        with get_db() as conn:
            conn.execute(
                "INSERT INTO events(title, description, event_date) VALUES(?,?,?)",
                (title, description, event_date)
            )
 
        return jsonify({
            "Message": "Event Created",
            "Status Code": 200
        })
 
class ListEvents(Resource):
    def get(self):
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM events").fetchall()
 
        events = [dict(r) for r in rows]
 
        return jsonify({
            "Message": events,
            "Status Code": 200
        })
 
class RegisterEvent(Resource):
    def post(self):
        postedData = request.get_json()
 
        status_code = checkPostedData(postedData, "register")
        if status_code != 200:
            return jsonify({
                "Message": "Missing registration fields",
                "Status Code": status_code
            })
 
        name = postedData["name"]
        email = postedData["email"]
        event_id = postedData["event_id"]
 
        with get_db() as conn:
            conn.execute(
                "INSERT INTO registrations(name, email, event_id) VALUES(?,?,?)",
                (name, email, event_id)
            )
 
        return jsonify({
            "Message": "Registration Successful",
            "Status Code": 200
        })
 
# ================= ROUTES =================
api.add_resource(CreateEvent, "/create_event")  #POST - http://127.0.0.1:5002/create_event
api.add_resource(ListEvents, "/events") #GET - http://127.0.0.1:5002/events
api.add_resource(RegisterEvent, "/register_event") #POST - http://127.0.0.1:5002/register_event
 
@app.route('/')
def home():
    return "Event Registration API Running"
 
if __name__ == "__main__":
    init_db()
    app.run(port=5002, debug=True)