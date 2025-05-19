from flask import Flask, render_template, request, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, json
from datetime import datetime
from scrape_and_save import scrape_and_save
import requests

app = Flask(__name__)
app.secret_key = "your-secret-key"  # 세션 유지 필수
GOOGLE_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"

# 사용자 DB 초기화
def init_user_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/users.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
init_user_db()

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        conn = sqlite3.connect("data/users.db")
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except:
            return "이미 존재하는 사용자입니다."
        finally:
            conn.close()
        return redirect("/login")
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("data/users.db")
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        conn.close()
        if row and check_password_hash(row[0], password):
            session["user"] = username
            return redirect("/")
        return "로그인 실패"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

@app.route("/")
def home():
    user = session.get("user")
    return render_template("index.html", user=user)

@app.route("/input", methods=["GET", "POST"])
def input_page():
    if "user" not in session:
        return redirect("/login")

    username = session.get("user")
    db_path = "data/spending.db"
    os.makedirs("data", exist_ok=True)

    if request.method == "POST":
        place = request.form["place"]
        amount = int(request.form["amount"])
        category = request.form["category"]
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS spending (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                date TEXT,
                place TEXT,
                amount INTEGER,
                category TEXT
            )
        """)
        cur.execute("INSERT INTO spending (username, date, place, amount, category) VALUES (?, ?, ?, ?, ?)",
                    (username, date, place, amount, category))
        conn.commit()
        conn.close()
        return redirect("/input")

    selected_date = request.args.get("date")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS spending (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            date TEXT,
            place TEXT,
            amount INTEGER,
            category TEXT
        )
    """)
    if selected_date:
        cur.execute("SELECT date, place, amount, category FROM spending WHERE username = ? AND date LIKE ?",
                    (username, f"{selected_date}%"))
    else:
        cur.execute("SELECT date, place, amount, category FROM spending WHERE username = ? ORDER BY date DESC LIMIT 20",
                    (username,))
    records = cur.fetchall()
    conn.close()

    return render_template("input.html", records=records, user=username)

@app.route("/stats")
def stats():
    if "user" not in session:
        return redirect("/login")
    user = session.get("user")
    return render_template("stats.html", user=user)

@app.route("/stats/detail")
def stats_detail():
    if "user" not in session:
        return redirect("/login")
    user = session.get("user")
    conn = sqlite3.connect("data/spending.db")
    cur = conn.cursor()
    cur.execute("SELECT date, place, amount, category FROM spending WHERE username = ? ORDER BY date DESC", (user,))
    records = cur.fetchall()
    conn.close()
    return render_template("stats_detail.html", records=records, user=user)

@app.route("/budget", methods=["GET", "POST"])
def budget():
    if "user" not in session:
        return redirect("/login")
    user = session.get("user")
    os.makedirs("data", exist_ok=True)
    user_budget_path = f"data/budget_{user}.json"

    if request.method == "POST":
        amount = request.form.get("amount")
        with open(user_budget_path, "w", encoding="utf-8") as f:
            json.dump({"amount": amount}, f, ensure_ascii=False, indent=2)
        return redirect("/budget")

    if os.path.exists(user_budget_path):
        with open(user_budget_path, "r", encoding="utf-8") as f:
            budget = json.load(f)
        monthly_budget = int(budget.get("amount", 0))
    else:
        budget = {"amount": ""}
        monthly_budget = 0

    current_month = datetime.now().strftime("%Y-%m")
    conn = sqlite3.connect("data/spending.db")
    cur = conn.cursor()
    cur.execute("SELECT SUM(amount) FROM spending WHERE username = ? AND date LIKE ?", (user, f"{current_month}%",))
    row = cur.fetchone()
    conn.close()

    monthly_spending = row[0] if row[0] else 0
    remaining = monthly_budget - monthly_spending
    is_over = remaining < 0

    return render_template("budget.html", budget=budget, monthly_spending=monthly_spending,
                           remaining=remaining, is_over=is_over, user=user)

@app.route("/wishlist")
def wishlist():
    if "user" not in session:
        return redirect("/login")
    user = session.get("user")

    # 사용자별 찜한 식당 파일 경로
    fav_file = f"data/favorites_{user}.json"

    try:
        with open(fav_file, "r", encoding="utf-8") as f:
            favorites = json.load(f)
    except:
        favorites = []

    try:
        with open("data/events.json", "r", encoding="utf-8") as f:
            events = json.load(f)
    except:
        events = []

    event_names = {e["name"] for e in events}

    enriched = []
    for item in favorites:
        enriched.append({
            "name": item["name"],
            "has_event": item["name"] in event_names
        })

    return render_template("wishlist.html", wishlist=enriched, user=user)

@app.route("/map")
def map_page():
    if "user" not in session:
        return redirect("/login")
    user = session.get("user")
    return render_template("map.html", user=user)


@app.route("/events")
def events():
    if "user" not in session:
        return redirect("/login")
    user = session.get("user")

    try:
        with open("data/events.json", "r", encoding="utf-8") as f:
            events = json.load(f)
    except:
        events = []

    return render_template("events.html", events=events, user=user)

# 📍 여기에 붙여넣기 시작
@app.route("/nearby")
def nearby():
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": 500,
        "type": "restaurant",
        "key": "AIzaSyCvBexqJOsexHnjdzpbUgFuMrrWCqhA-Y8"
    }

    response = requests.get(url, params=params)
    data = response.json()

    places = []
    for result in data.get("results", []):
        places.append({
            "name": result.get("name"),
            "lat": result["geometry"]["location"]["lat"],
            "lng": result["geometry"]["location"]["lng"]
        })

    return jsonify(places)

@app.route("/favorite", methods=["POST"])
def favorite():
    if "user" not in session:
        return jsonify({"success": False, "error": "로그인이 필요합니다."})

    data = request.get_json()
    user = session["user"]
    fav_file = f"data/favorites_{user}.json"

    try:
        if os.path.exists(fav_file):
            with open(fav_file, "r", encoding="utf-8") as f:
                favorites = json.load(f)
        else:
            favorites = []

        # 중복 방지
        if not any(f["name"] == data["name"] for f in favorites):
            favorites.append(data)

        with open(fav_file, "w", encoding="utf-8") as f:
            json.dump(favorites, f, ensure_ascii=False, indent=2)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)

