import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    database_path = tmp_path / "test.db"
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "DATABASE_PATH": str(database_path),
        }
    )
    with app.app_context():
        from database import get_db
        db = get_db(str(database_path))
        db.execute("DELETE FROM tasks")
        db.execute("DELETE FROM users")
        db.commit()
        db.close()

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def register(client, username="alice", password="correct-horse-battery-staple"):
    return client.post(
        "/signup",
        data={
            "username": username,
            "password": password,
            "confirm_password": password,
        },
        follow_redirects=True,
    )
