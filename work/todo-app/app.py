import os
import secrets
import tempfile
from functools import wraps

import bcrypt
from dotenv import load_dotenv
from flask import Flask, flash, g, redirect, render_template, request, session, url_for

from database import get_db as connect_db
from database import initialize_database


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32)),
        DATABASE_PATH=os.getenv("DATABASE_PATH", os.path.join(tempfile.gettempdir(), "taskflow.db")),
        TESTING=False,
    )
    if test_config:
        app.config.update(test_config)

    initialize_database(app.config["DATABASE_PATH"])

    def get_current_user_id():
        return session.get("user_id")

    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if get_current_user_id() is None:
                return redirect(url_for("login", next=request.path))
            return view(*args, **kwargs)

        return wrapped

    @app.teardown_appcontext
    def close_database(exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    @app.context_processor
    def inject_user():
        return {"current_user": get_current_user_id()}

    def get_db():
        if "db" not in g:
            g.db = connect_db(app.config["DATABASE_PATH"])
        return g.db

    @app.get("/")
    def index():
        if get_current_user_id() is None:
            return redirect(url_for("login"))
        return redirect(url_for("tasks"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "GET":
            return render_template("login.html")

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("login.html"), 400

        db = get_db()
        user = db.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if user is None or not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"]):
            flash("Invalid username or password.", "error")
            return render_template("login.html"), 401

        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        flash("Welcome back!", "success")
        return redirect(url_for("tasks"))

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "GET":
            return render_template("signup.html")

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("signup.html"), 400
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return render_template("signup.html"), 400
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("signup.html"), 400

        db = get_db()
        existing = db.execute(
            "SELECT 1 FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if existing:
            flash("That username is already registered.", "error")
            return render_template("signup.html"), 409

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
        cursor = db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        db.commit()
        session.clear()
        session["user_id"] = cursor.lastrowid
        session["username"] = username
        flash("Account created successfully.", "success")
        return redirect(url_for("tasks"))

    @app.post("/logout")
    @login_required
    def logout():
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for("login"))

    @app.route("/tasks", methods=["GET", "POST"])
    @login_required
    def tasks():
        user_id = get_current_user_id()
        db = get_db()

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            if not title:
                flash("Task title cannot be empty.", "error")
                return redirect(url_for("tasks"))

            db.execute(
                "INSERT INTO tasks (user_id, title) VALUES (?, ?)",
                (user_id, title),
            )
            db.commit()
            flash("Task added.", "success")
            return redirect(url_for("tasks"))

        rows = db.execute(
            "SELECT id, title, completed, created_at FROM tasks "
            "WHERE user_id = ? ORDER BY created_at DESC, id DESC",
            (user_id,),
        ).fetchall()
        return render_template("tasks.html", tasks=rows)

    @app.post("/tasks/<int:task_id>/toggle")
    @login_required
    def toggle_task(task_id):
        user_id = get_current_user_id()
        db = get_db()
        row = db.execute(
            "SELECT completed FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id),
        ).fetchone()
        if row is None:
            return render_template("not_found.html"), 404

        db.execute(
            "UPDATE tasks SET completed = ? WHERE id = ? AND user_id = ?",
            (not row["completed"], task_id, user_id),
        )
        db.commit()
        flash("Task updated.", "success")
        return redirect(url_for("tasks"))

    @app.post("/tasks/<int:task_id>/delete")
    @login_required
    def delete_task(task_id):
        user_id = get_current_user_id()
        db = get_db()
        cursor = db.execute(
            "DELETE FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id),
        )
        db.commit()
        if cursor.rowcount == 0:
            return render_template("not_found.html"), 404

        flash("Task deleted.", "success")
        return redirect(url_for("tasks"))

    @app.get("/not-found")
    def not_found():
        return render_template("not_found.html"), 404

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("not_found.html"), 404

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
