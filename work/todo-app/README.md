# TaskFlow

TaskFlow is a secure, personal to-do web application built with Flask, SQLite, and bcrypt. Each authenticated user can add, complete, and delete only their own tasks.

## Features

- Account registration and login with hashed passwords.
- Session-based authentication.
- SQLite persistence.
- User-scoped task listing, completion, and deletion.
- Validation that rejects empty or whitespace-only task titles.
- Responsive, accessible web interface.
- Automated tests for authentication and task isolation.

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Copy the example environment file:

   ```bash
   copy .env.example .env
   ```

4. Replace `FLASK_SECRET_KEY` in `.env` with a long random value. The application generates a key if one is omitted, but a fixed key is recommended for deployed environments.
5. Start the application:

   ```bash
   flask --app app run
   ```

6. Open `http://127.0.0.1:5000` and create an account.

## Database

The application creates `todo.db` automatically. The schema uses foreign keys and a `tasks.user_id` relationship to `users.id`. Every task query and mutation includes the authenticated user's ID.

## Tests

Run the full test suite:

```bash
python -m pytest
```

Tests use a temporary SQLite database and exercise real Flask routes and database behavior.

## Security notes

- Passwords are stored only as bcrypt hashes.
- The `.env` file and SQLite database files are excluded from Git.
- Flask sessions are signed and stored server-side by default.
- Task reads, updates, and deletes are explicitly scoped to the logged-in user.
- The application uses parameterized SQL queries to prevent SQL injection.
