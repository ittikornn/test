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

## Deploy to Vercel

1. Push the project to GitHub.
2. Import the repository into Vercel.
3. Select **Python** as the framework preset, or use the included `vercel.json` configuration.
4. Set `FLASK_SECRET_KEY` in the Vercel environment variables.
5. Deploy the project.

The Vercel deployment uses the included Flask handler. SQLite data is temporary and may not survive function redeployments.

## Database

The application creates `todo.db` automatically. The schema uses foreign keys and a `tasks.user_id` relationship to `users.id`. Every task query and mutation includes the authenticated user's ID.

> SQLite is suitable for this demonstration, but production deployments should use a hosted database with persistent storage, backups, and managed security controls. A serverless platform such as Vercel may not preserve SQLite data across deployments.

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
