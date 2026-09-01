---
# Spec: Registration

## Overview
Registration allows a new user to sign up for Spendly. Users provide a name, email and password. The system stores the new user in the *users* table with a hashed password, and redirects to the login page or home page. This step completes the initial user flow and is required for any subsequent expense‑tracking features.

## Depends on
- **1. Database setup** – The *users* table must exist with the columns `name`, `email`, `password_hash`, `created_at`.

## Routes
- `GET /register` – render the registration form (already present).
- `POST /register` – process the form data, validate input, create a new user record, and redirect to `/login`.
- `GET /login` – unchanged.


## Database changes
No new tables or columns – only inserting a row into the existing `users` table.

## Templates
- **Create**: `/templates/register.html` already exists but should be updated.
- **Modify**: `/templates/base.html` remains the master layout.

`register.html` should extend `base.html` and contain a simple form with fields: `name`, `email`, `password`, and a submit button.

## Files to change
- `app.py` – add a `POST /register` handler and the redirect logic.
- `templates/register.html` – add the actual form.

## Files to create
- None.

## New dependencies
No new pip packages.

## Rules for implementation
- No ORM – use `sqlite3` directly.
- All SQL must use `?` placeholders – never interpolate data.
- Passwords must be hashed with `werkzeug.security.generate_password_hash`.
- Use CSS variables for colors – do not hard‑code hex values.
- All templates must extend `base.html`.
- The view should use `abort(400)` for form validation errors.

## Definition of Done
- Visiting `/register` displays a working form.
- Submitting the form with valid data creates a new user in the database.
- The password is stored as a hash.
- After registration the user is redirected to the login page.
- No SQL injection is possible.
- All tests for the registration route pass.
---