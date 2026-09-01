# database/db.py
"""SQLite helpers for the Spendly app.

This module contains three public functions:

* :func:`get_db` – obtain a SQLite connection with ``row_factory`` set to ``sqlite3.Row`` and foreign‑key enforcement turned on.
* :func:`init_db` – create the *users* and *expenses* tables if they are missing.
* :func:`seed_db` – populate the database with a demo user and eight sample expenses the first time the app starts.

All operations use parameterised SQL (``?`` placeholders) to prevent injection.  The module is intentionally lightweight and does not depend on any external packages beyond the Python standard library and :mod:`werkzeug`.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timedelta
from typing import Iterable, Tuple

from werkzeug.security import generate_password_hash

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# The SQLite file lives in the project root (one level above the database
# package).  ``__file__`` points to ``database/db.py``. ``os.path.realpath``
# ensures we resolve any symlinks that may exist in the execution environment.
ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
_DB_PATH = os.path.join(ROOT_DIR, "spendly.db")  # fixture name from spec

# --- Public API ------------------------------------------------------------

def get_db() -> sqlite3.Connection:
    """Return a SQLite connection for the Spendly database.

    The connection is configured with:

    * ``row_factory = sqlite3.Row`` – rows act like dicts.
    * ``PRAGMA foreign_keys = ON`` – enforce FK constraints.
    """
    conn = sqlite3.connect(_DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create the required tables if they do not already exist.

    The schema is strictly defined in the project spec.  ``CREATE TABLE IF
    NOT EXISTS`` guarantees the operation is safe to run repeatedly.
    """
    conn = get_db()
    cur = conn.cursor()

    # Users table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );
        """
    )

    # Expenses table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )

    conn.commit()


def _demo_user_exists(cur: sqlite3.Cursor) -> bool:
    """Return True if the users table contains at least one row."""
    cur.execute("SELECT EXISTS(SELECT 1 FROM users) AS exists_flag;")
    return bool(cur.fetchone()["exists_flag"])


def seed_db() -> None:
    """Populate the database with demo data if it hasn't been seeded yet.

    Seed logic is idempotent: it exits immediately if the ``users`` table
    already has data.  The demo user is always the same and the eight
    expenses are linked to that user.  Passwords are stored using a
    Werk­zeug hash.
    """
    conn = get_db()
    cur = conn.cursor()

    if _demo_user_exists(cur):
        # Data already present – do nothing.  This keeps the function safe on
        # subsequent app restarts.
        return

    # Demo user data
    demo_email = "demo@spendly.com"
    demo_password = "demo123"
    hashed = generate_password_hash(demo_password)

    cur.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", demo_email, hashed),
    )
    user_id = cur.lastrowid

    # Sample expenses – cover each category
    categories = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]
    today = datetime.now().date()
    expenses: Iterable[Tuple[float, str, str, str, str]] = [
        # amount, category, date, description
        (12.30, "Food", today.isoformat(), "Coffee at cafe"),
        (3.50, "Transport", (today - timedelta(days=1)).isoformat(), "Bus fare"),
        (45.00, "Bills", (today - timedelta(days=3)).isoformat(), "Electricity bill"),
        (9.99, "Health", (today - timedelta(days=5)).isoformat(), "Drugstore"),
        (22.00, "Entertainment", (today - timedelta(days=7)).isoformat(), "Movie tickets"),
        (65.00, "Shopping", (today - timedelta(days=10)).isoformat(), "Clothes"),
        (5.00, "Other", (today - timedelta(days=12)).isoformat(), "Misc"),
        (3.00, "Food", (today - timedelta(days=14)).isoformat(), "Lunch"),
    ]

    # Insert expenses
    cur.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        [(user_id, amt, cat, d, desc) for amt, cat, d, desc in expenses],
    )

    conn.commit()

# If this module is executed directly, run a quick demo of seeding.
if __name__ == "__main__":
    init_db()
    seed_db()
    print(f"Database initialized at {_DB_PATH}")
