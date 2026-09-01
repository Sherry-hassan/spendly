# Spec: Login and Logout

## Overview
The Login and Logout feature implements user authentication for the Spendly expense tracker. It adds ability for registered users to log in and terminate their session, protecting sensitive pages like the profile and expense management routes.

## Depends on
- Step 2 – User Registration (ensures a users table with hashed passwords exists). 
- The database schema (see `database/db.py`) must already provide a `users` table with `email` and `password_hash` columns.

## Routes
- `GET /login` – Render the existing `login.html` template (public).
- `POST /login` – Process submitted credentials.
  - Validates email and password against the `users` table.
  - On success: sets `session['user_id']` and redirects to `/profile`.
  - On failure: aborts with HTTP 401 and an informative message.
- `GET /logout` – Clear the user session and redirect to the login page.

> **Access level**: `login` is public, `logout` requires a logged‑in user (enforced by checking `session['user_id']`).

## Database changes
No new tables or columns are required for this feature. The existing `users` table is sufficient.

## Templates
- **Create**: None.
- **Modify**: `templates/login.html` if you wish to add a “Login” form; existing template already provides a form with fields `email` and `password`.

## Files to change
- `app.py` (add POST handling to `/login`, add session setup, import `check_password_hash`, implement `/logout`).

## Files to create
- None.

## New dependencies
- No new pip packages. Authentication uses Flask's built‑in session and Werkzeug's security helpers already present.

## Rules for implementation
- **No ORM**: use raw SQLite queries with `?` placeholders.
- **Password hashing**: use `werkzeug.security.check_password_hash` for verification.
- **Session management**: set `app.secret_key` (a hard‑coded key or `os.getenv('FLASK_SECRET')`).
- **Redirects**: after successful login redirect to `url_for('profile')`; after logout redirect to `url_for('login')`.
- **Security**: never return plain password or store it in session.

## Definition of done
- `GET /login` renders the login form.
- Successful POST /login authenticates user, stores `user_id` in session, and redirects to `/profile`.
- Failed POST /login returns 401 and a useful error message.
- `GET /logout` clears the session and redirects to the login page.
- All routes respect the access level conventions.
- No deprecations or security warnings appear in the tests.
