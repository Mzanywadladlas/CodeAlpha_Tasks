from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flasgger import Swagger
import sqlite3

app = Flask(__name__)
bcrypt = Bcrypt(app)
swagger = Swagger(app)

# -----------------------------
# INITIALIZE DATABASE
# -----------------------------
def init_db():
    conn = sqlite3.connect("events.db")
    c = conn.cursor()

    # USERS TABLE
    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        );
    """)

    # EVENTS TABLE
    c.execute("""
        CREATE TABLE IF NOT EXISTS events(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            date TEXT
        );
    """)

    # REGISTRATIONS TABLE
    c.execute("""
        CREATE TABLE IF NOT EXISTS registrations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            event_id INTEGER
        );
    """)

    conn.commit()
    conn.close()

init_db()

# -----------------------------
# AUTHENTICATION ROUTES
# -----------------------------
@app.post("/register")
def register():
    """
    Register user
    ---
    parameters:
      - name: username
        in: formData
        required: true
      - name: password
        in: formData
        required: true
    """
    username = request.form["username"]
    password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")

    try:
        conn = sqlite3.connect("events.db")
        c = conn.cursor()
        c.execute("INSERT INTO users(username, password) VALUES (?,?)", (username, password))
        conn.commit()
        return {"message": "User registered!"}
    except:
        return {"error": "Username already exists"}, 400


@app.post("/login")
def login():
    """
    Login user
    ---
    parameters:
      - name: username
        in: formData
        required: true
      - name: password
        in: formData
        required: true
    """
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("events.db")
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE username=?", (username,))
    user = c.fetchone()

    if user and bcrypt.check_password_hash(user[1], password):
        return {"message": "Login successful", "user_id": user[0]}

    return {"error": "Invalid login"}, 401

# -----------------------------
# EVENT MANAGEMENT (CRUD)
# -----------------------------
@app.post("/events")
def create_event():
    """
    Create new event
    ---
    parameters:
      - name: title
        in: formData
        required: true
      - name: description
        in: formData
        required: true
      - name: date
        in: formData
        required: true
    """
    title = request.form["title"]
    description = request.form["description"]
    date = request.form["date"]

    conn = sqlite3.connect("events.db")
    c = conn.cursor()
    c.execute("INSERT INTO events(title, description, date) VALUES (?,?,?)",
              (title, description, date))
    conn.commit()

    return {"message": "Event created!"}


@app.get("/events")
def list_events():
    """
    List all events
    ---
    """
    conn = sqlite3.connect("events.db")
    c = conn.cursor()
    c.execute("SELECT * FROM events")
    events = [{"id": e[0], "title": e[1], "description": e[2], "date": e[3]} for e in c.fetchall()]

    return {"events": events}


@app.get("/events/<int:event_id>")
def event_details(event_id):
    """
    Get event details
    ---
    """
    conn = sqlite3.connect("events.db")
    c = conn.cursor()
    c.execute("SELECT * FROM events WHERE id=?", (event_id,))
    event = c.fetchone()

    if event:
        return {
            "id": event[0],
            "title": event[1],
            "description": event[2],
            "date": event[3]
        }

    return {"error": "Event not found"}, 404

# -----------------------------
# EVENT REGISTRATION
# -----------------------------
@app.post("/register_event")
def register_event():
    """
    Register user for event
    ---
    parameters:
      - name: user_id
        in: formData
        required: true
      - name: event_id
        in: formData
        required: true
    """
    user_id = request.form["user_id"]
    event_id = request.form["event_id"]

    conn = sqlite3.connect("events.db")
    c = conn.cursor()

    c.execute("INSERT INTO registrations(user_id, event_id) VALUES (?,?)",
              (user_id, event_id))
    conn.commit()

    return {"message": "Registered for event!"}


@app.post("/cancel_registration")
def cancel_registration():
    """
    Cancel event registration
    ---
    parameters:
      - name: user_id
        in: formData
        required: true
      - name: event_id
        in: formData
        required: true
    """
    user_id = request.form["user_id"]
    event_id = request.form["event_id"]

    conn = sqlite3.connect("events.db")
    c = conn.cursor()
    c.execute("DELETE FROM registrations WHERE user_id=? AND event_id=?",
              (user_id, event_id))
    conn.commit()

    return {"message": "Registration cancelled!"}


@app.get("/my_events/<int:user_id>")
def my_events(user_id):
    """
    List events a user is registered for
    ---
    """
    conn = sqlite3.connect("events.db")
    c = conn.cursor()

    c.execute("""
        SELECT events.id, events.title, events.description, events.date
        FROM events
        JOIN registrations ON events.id = registrations.event_id
        WHERE registrations.user_id=?;
    """, (user_id,))

    events = [{"id": e[0], "title": e[1], "description": e[2], "date": e[3]}
              for e in c.fetchall()]

    return {"registered_events": events}

if __name__ == "__main__":
    app.run(debug=True)