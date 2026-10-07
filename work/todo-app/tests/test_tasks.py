def create_user(client, username="alice", password="correct-horse-battery-staple"):
    response = client.post(
        "/signup",
        data={
            "username": username,
            "password": password,
            "confirm_password": password,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_user_can_add_and_list_tasks(client):
    create_user(client)

    response = client.post(
        "/tasks",
        data={"title": "Buy milk"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Buy milk" in response.data
    assert b"Task added" in response.data


def test_task_title_cannot_be_empty_or_whitespace(client):
    create_user(client)

    for title in ("", "   "):
        response = client.post(
            "/tasks",
            data={"title": title},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Task title cannot be empty" in response.data


def test_user_can_complete_and_delete_a_task(client):
    create_user(client)
    client.post("/tasks", data={"title": "Review notes"}, follow_redirects=True)

    task_id = client.get("/tasks").data.find(b"Review notes")
    assert task_id >= 0

    response = client.post("/tasks/1/toggle", follow_redirects=True)
    assert response.status_code == 200
    assert b"Task updated" in response.data

    response = client.post("/tasks/1/delete", follow_redirects=True)
    assert response.status_code == 200
    assert b"Task deleted" in response.data
    assert b"Review notes" not in response.data


def test_task_operations_are_scoped_to_the_logged_in_user(client):
    create_user(client, "alice")
    client.post("/tasks", data={"title": "Alice task"}, follow_redirects=True)
    client.post("/logout")
    create_user(client, "bob")

    alice_task_response = client.get("/tasks")
    assert b"Alice task" not in alice_task_response.data

    response = client.post("/tasks/1/toggle", follow_redirects=True)
    assert response.status_code == 404

    response = client.post("/tasks/1/delete", follow_redirects=True)
    assert response.status_code == 404


def test_task_delete_rejects_unknown_task_for_current_user(client):
    create_user(client)

    response = client.post("/tasks/999/delete", follow_redirects=True)

    assert response.status_code == 404
    assert b"Task not found" in response.data
