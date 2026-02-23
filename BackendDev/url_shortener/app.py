from flask import Flask, request, jsonify, redirect
from flask_bcrypt import Bcrypt
import sqlite3
from flasgger import Swagger

app = Flask(__name__)
bcrypt = Bcrypt(app)
swagger = Swagger(app)

# -------------------------
# DATABASE INITIALIZATION
# -------------------------
def init_db():
    conn = sqlite3.connect("urls.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        );
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS urls(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            short_code TEXT UNIQUE,
            long_url TEXT
        );
    """)

    conn.commit()
    conn.close()

init_db()

# -------------------------
# AUTH ROUTES
# -------------------------
@app.post("/register")
def register():
    """
    Register new user
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
        conn = sqlite3.connect("urls.db")
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

    conn = sqlite3.connect("urls.db")
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE username=?", (username,))
    user = c.fetchone()

    if user and bcrypt.check_password_hash(user[1], password):
        return {"message": "Login successful", "user_id": user[0]}

    return {"error": "Invalid credentials"}, 401

# -------------------------
# URL SHORTENER ROUTES
# -------------------------
@app.post("/shorten")
def shorten_url():
    """
    Create short URL
    ---
    parameters:
      - name: user_id
        in: formData
        required: true
      - name: long_url
        in: formData
        required: true
    """
    import random, string

    user_id = request.form["user_id"]
    long_url = request.form["long_url"]
    code = "".join(random.choices(string.ascii_letters + string.digits, k=6))

    conn = sqlite3.connect("urls.db")
    c = conn.cursor()
    c.execute("INSERT INTO urls(user_id, short_code, long_url) VALUES (?,?,?)",
              (user_id, code, long_url))
    conn.commit()

    return {"short_url": f"http://localhost:5000/{code}"}


@app.get("/<code>")
def redirect_url(code):
    conn = sqlite3.connect("urls.db")
    c = conn.cursor()
    c.execute("SELECT long_url FROM urls WHERE short_code=?", (code,))
    result = c.fetchone()

    if result:
        return redirect(result[0])
    return {"error": "URL not found"}, 404

if __name__ == "__main__":
    app.run(debug=True)