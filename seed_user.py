#!/usr/bin/env python3
"""Script to create a realistic random Indian user in spendly.db.

This script demonstrates the same pattern used in ``database/db.py`` for
``get_db`` and for inserting data.
"""

from __future__ import annotations

import random
from datetime import datetime

from werkzeug.security import generate_password_hash

# Import the real database helpers from the app
from database.db import get_db, init_db

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def random_indian_name() -> str:
    """Return a realistic first + last name for an Indian user."""
    firsts = [
        "Arjun",
        "Rahul",
        "Deepak",
        "Amit",
        "Nisha",
        "Priya",
        "Sanjay",
        "Neha",
        "Karthik",
        "Mahesh",
        "Ravi",
        "Sangeetha",
        "Jaya",
        "Nandakumar",
        "Lakshmi",
        "Rout",
        "Bijoy",
        "Kumar",
        "Sutapa",
        "Shah",
        "Amrit",
        "Gayatri",
        "Rajesh",
    ]
    lasts = [
        "Sharma",
        "Singh",
        "Patel",
        "Kumar",
        "Nair",
        "Reddy",
        "Jain",
        "Gupta",
        "Mohanty",
        "Gopi",
        "Iyer",
    ]
    return f"{random.choice(firsts)} {random.choice(lasts)}"


def random_email(name: str) -> str:
    """Create an email from a name with a random 2‑3 digit suffix."""
    local = name.lower().replace(" ", ".")
    suffix = str(random.randint(10, 999))
    return f"{local}{suffix}@gmail.com"


def ensure_unique_email(cur, email: str) -> str:
    """Return an email that does not yet exist in the ``users`` table."""
    cur.execute("SELECT 1 FROM users WHERE email = ? LIMIT 1", (email,))
    while cur.fetchone():
        email = random_email(random_indian_name())
        cur.execute("SELECT 1 FROM users WHERE email = ? LIMIT 1", (email,))
    return email

# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def seed_user():
    # Ensure database tables exist
    init_db()
    conn = get_db()
    cur = conn.cursor()

    name = random_indian_name()
    email = random_email(name)
    email = ensure_unique_email(cur, email)
    password = "password123"
    hashed = generate_password_hash(password)
    created_at = datetime.now().isoformat()

    cur.execute(
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (name, email, hashed, created_at),
    )
    conn.commit()
    user_id = cur.lastrowid
    print(f"User created:\n  id: {user_id}\n  name: {name}\n  email: {email}")


if __name__ == "__main__":
    seed_user()
