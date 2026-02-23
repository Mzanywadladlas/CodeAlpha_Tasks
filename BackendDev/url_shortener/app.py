from flask import Flask, jsonify, request, redirect
from flask_restful import Api, Resource
import sqlite3
import string
import random
from urllib.parse import urlparse
from pathlib import Path
 
app = Flask(__name__)
api = Api(app)
 
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "urls.db"
 
# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
 
def init_db():
    with get_db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS urls(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            original_url TEXT,
            hits INTEGER DEFAULT 0
        )
        """)
 
# ================= VALIDATION =================
def checkPostedData(postedData, functionName):
    if functionName == "shorten":
        if "url" not in postedData:
            return 301
        elif not is_valid_url(postedData["url"]):
            return 302
        else:
            return 200
    return 200
 
def is_valid_url(value):
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and parsed.netloc
    except:
        return False
 
# ================= SERVICE =================
def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))
 
def code_exists(code):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM urls WHERE code=?",
            (code,)
        ).fetchone()
        return row is not None
 
def create_unique_code():
    while True:
        code = generate_code()
        if not code_exists(code):
            return code
 
# ================= RESOURCES =================
class Shorten(Resource):
    def post(self):
        postedData = request.get_json()
 
        status_code = checkPostedData(postedData, "shorten")
        if status_code != 200:
            return jsonify({
                "Message": "Invalid URL or missing field",
                "Status Code": status_code
            })
 
        url = postedData["url"]
        code = create_unique_code()
 
        with get_db() as conn:
            conn.execute(
                "INSERT INTO urls(code, original_url) VALUES(?,?)",
                (code, url)
            )
 
        short_url = request.host_url + code
 
        return jsonify({
            "Message": short_url,
            "Status Code": 200
        })
 
class RedirectURL(Resource):
    def get(self, code):
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM urls WHERE code=?",
                (code,)
            ).fetchone()
 
        if not row:
            return jsonify({
                "Message": "URL not found",
                "Status Code": 404
            })
 
        with get_db() as conn:
            conn.execute(
                "UPDATE urls SET hits = hits + 1 WHERE code=?",
                (code,)
            )
 
        return redirect(row["original_url"])
 
# ================= ROUTES =================
api.add_resource(Shorten, "/shorten")
api.add_resource(RedirectURL, "/<string:code>")
 
@app.route('/')
def home():
    return "URL Shortener API Running"
 
if __name__ == "__main__":
    init_db()
    app.run(port=5001, debug=True)