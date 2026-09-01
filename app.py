from flask import Flask, render_template, request, redirect, url_for, abort, session
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'dev-secret')

# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():

    welcome_message = None
    if "user_id" in session:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT name FROM users WHERE id = ?", (session['user_id'],))
        row = cur.fetchone()
        if row:
            welcome_message = f"Welcome back, {row['name']}!"
    return render_template("landing.html", welcome_message=welcome_message)

@app.route("/register", methods=["GET", "POST"])

def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        if not all([name, email, password]):
            abort(400, "Missing required fields")
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        if cur.fetchone():
            abort(400, "Email already registered")
        hashed = generate_password_hash(password)
        cur.execute(
            "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, datetime('now'))",
            (name, email, hashed),
        )
        conn.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])

def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not all([email, password]):
            abort(400, "Missing required fields")
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, password_hash FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        if row is None or not check_password_hash(row['password_hash'], password):
            abort(401, "Invalid credentials")
        session['user_id'] = row['id']
        return redirect(url_for("landing"))
    return render_template("login.html")

@app.route("/terms")

def terms():
    return render_template("terms.html")

@app.route("/privacy")

def privacy():
    return render_template("privacy.html")

# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")

def logout():
    if "user_id" not in session:
        abort(401, "Not logged in")
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/profile")

def profile():
    return "Profile page — coming in Step 4"

@app.route("/expenses/add")

def add_expense():
    return "Add expense — coming in Step 7"

@app.route("/expenses/<int:id>/edit")

def edit_expense(id):
    return "Edit expense — coming in Step 8"

@app.route("/expenses/<int:id>/delete")

def delete_expense(id):
    return "Delete expense — coming in Step 9"

from database.db import init_db, seed_db, get_db

if __name__ == "__main__":
    # Ensure database is ready before the first request
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
