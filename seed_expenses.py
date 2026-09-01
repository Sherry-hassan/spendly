#!/usr/bin/env python3
"""Seed the spendly database with fake expenses for a given user.

This script is designed to be run from the project root where ``database/db.py``
is located.

Usage:
    python seed_expenses.py <user_id> <count> <months>
"""

from __future__ import annotations

import sys
import random
from datetime import datetime, timedelta

import sqlite3

# Import the real database helpers
from database.db import get_db, init_db

# ---------------------------------------------------------------------------
# Configuration – category ranges (in INR)
# ---------------------------------------------------------------------------
CATEGORIES = {
    "Food": (50, 800),
    "Transport": (20, 500),
    "Bills": (200, 3000),
    "Health": (100, 2000),
    "Entertainment": (100, 1500),
    "Shopping": (200, 5000),
    "Other": (50, 1000),
}
# Weights approximate relative frequency
CATEGORY_WEIGHTS = [
    0.40,  # Food
    0.20,  # Transport
    0.12,  # Bills
    0.08,  # Health
    0.08,  # Entertainment
    0.07,  # Shopping
    0.05,  # Other
]

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def parse_args(argv):
    if len(argv) != 3:
        return None
    try:
        return tuple(int(v) for v in argv)
    except ValueError:
        return None


def user_exists(conn: sqlite3.Connection, user_id: int) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE id = ?", (user_id,))
    return bool(cur.fetchone())


def random_date_within(months: int) -> datetime:
    days = random.randint(0, months * 30)
    return datetime.now() - timedelta(days=days)


def generate_expense(user_id: int) -> tuple:
    """Return a tuple ready for insertion.

    (user_id, amount, category, date_str, description, created_at)
    """
    category = random.choices(list(CATEGORIES.keys()), weights=CATEGORY_WEIGHTS, k=1)[0]
    low, high = CATEGORIES[category]
    amount = round(random.uniform(low, high), 2)
    date = random_date_within(args[2])  # use global args for months
    date_str = date.date().isoformat()
    created_at = datetime.now().isoformat()
    # Simple description using a sample phrase per category
    DESCRIPTIONS = {
        "Food": ["Lunch", "Coffee", "Dinner", "Snacks", "Street food"],
        "Transport": ["Bus fare", "Metro", "Taxi", "Rental"],
        "Bills": ["Electricity bill", "Water bill", "Internet", "Phone"],
        "Health": ["Doctor visit", "Medication", "Lab tests"],
        "Entertainment": ["Movie tickets", "Concert", "Gym subscription"],
        "Shopping": ["Clothes", "Electronics", "Groceries", "Furniture"],
        "Other": ["Gift", "Charity", "Misc"],
    }
    description = f"{random.choice(DESCRIPTIONS[category])}"
    return (user_id, amount, category, date_str, description, created_at)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    if args is None:
        print("Usage: /seed-expenses <user_id> <count> <months>\nExample: /seed-expenses 1 50 6")
        sys.exit(1)

    user_id, count, months = args

    # Ensure tables exist and check user
    init_db()
    conn = get_db()
    if not user_exists(conn, user_id):
        print(f"No user found with id {user_id}.")
        sys.exit(1)

    expenses = [generate_expense(user_id) for _ in range(count)]

    # Insert in a single transaction
    try:
        cur = conn.cursor()
        cur.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            expenses,
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Failed to insert expenses:", e)
        sys.exit(1)

    # Gather info for confirmation
    dates = [exp[3] for exp in expenses]
    min_date, max_date = min(dates), max(dates)
    # Sample 5 records – newest first
    cur.execute("SELECT id, user_id, amount, category, date, description FROM expenses WHERE user_id = ? ORDER BY id DESC LIMIT 5", (user_id,))
    sample_rows = cur.fetchall()

    print(f"Inserted {count} expenses for user {user_id}.")
    print(f"Date range: {min_date} to {max_date}")
    print("Sample 5 records (most recent first):")
    for row in sample_rows:
        print(f"  id={row['id']}, amount={row['amount']}, cat={row['category']}, date={row['date']}, desc={row['description']}")
