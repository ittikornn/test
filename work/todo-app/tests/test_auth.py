from app import create_app


def test_login_accepts_valid_credentials(client):
    client.post(
        "/signup",
        data={
            "username": "alice",
            "password": "correct-horse-battery-staple",
            "confirm_password": "correct-horse-battery-staple",
        },
    )
    client.get("/logout")

    response = client.post(
        "/login",
        data={"username": "alice", "password": "correct-horse-battery-staple"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Welcome back!" in response.data
    assert b"My Tasks" in response.data


def test_login_rejects_invalid_credentials(client):
    client.post(
        "/signup",
        data={
            "username": "alice",
            "password": "correct-horse-battery-staple",
            "confirm_password": "correct-horse-battery-staple",
        },
    )
    client.get("/logout")

    response = client.post(
        "/login",
        data={"username": "alice", "password": "wrong-password"},
        follow_redirects=True,
    )

    assert response.status_code == 401
    assert b"Invalid username or password" in response.data


def test_task_pages_require_authentication(client):
    response = client.get("/tasks")

    assert response.status_code == 302
    assert response.headers["Location"].startswith("/login?")
    assert "next=/tasks" in response.headers["Location"]


def test_logout_clears_the_session(client):
    client.post(
        "/signup",
        data={
            "username": "alice",
            "password": "correct-horse-battery-staple",
            "confirm_password": "correct-horse-battery-staple",
        },
    )

    response = client.post("/logout", follow_redirects=True)

    assert response.status_code == 200
    assert b"You have been logged out" in response.data
    assert client.get("/tasks").status_code == 302
