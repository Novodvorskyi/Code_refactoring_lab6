import pytest
import mongomock
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(autouse=True)
def clean_db():
    from app import tasks_collection
    tasks_collection.delete_many({})
    yield
    tasks_collection.delete_many({})

@pytest.fixture
def client():
    """Create a test Flask client with a mocked MongoDB."""
    import app as app_module

    with patch.object(app_module, "MongoClient", mongomock.MongoClient):
        import importlib
        importlib.reload(app_module)

        app_module.app.config["TESTING"] = True

        with app_module.app.test_client() as c:
            yield c

# Health

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "ok"
    assert "timestamp" in data


#  GET /tasks

def test_get_tasks_empty(client):
    r = client.get("/tasks")
    assert r.status_code == 200
    assert r.get_json() == []


def test_get_tasks_after_create(client):
    client.post("/tasks", json={"title": "Buy milk", "description": "2% fat"})
    r = client.get("/tasks")
    assert r.status_code == 200
    tasks = r.get_json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Buy milk"


#  POST /tasks

def test_create_task_success(client):
    r = client.post("/tasks", json={"title": "Test task", "description": "desc"})
    assert r.status_code == 201
    data = r.get_json()
    assert data["title"] == "Test task"
    assert data["done"] is False
    assert "_id" in data


def test_create_task_missing_title(client):
    r = client.post("/tasks", json={"description": "no title"})
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_create_task_no_body(client):
    r = client.post("/tasks", content_type="application/json", data="")
    assert r.status_code == 400


#  GET /tasks/<id>

def test_get_task_by_id(client):
    created = client.post("/tasks", json={"title": "Find me"}).get_json()
    r = client.get(f"/tasks/{created['_id']}")
    assert r.status_code == 200
    assert r.get_json()["title"] == "Find me"


def test_get_task_not_found(client):
    r = client.get("/tasks/000000000000000000000000")
    assert r.status_code == 404


def test_get_task_invalid_id(client):
    r = client.get("/tasks/not-an-id")
    assert r.status_code == 400


# PUT /tasks/<id>

def test_update_task(client):
    created = client.post("/tasks", json={"title": "Old title"}).get_json()
    r = client.put(f"/tasks/{created['_id']}", json={"title": "New title", "done": True})
    assert r.status_code == 200
    data = r.get_json()
    assert data["title"] == "New title"
    assert data["done"] is True


def test_update_task_not_found(client):
    r = client.put("/tasks/000000000000000000000000", json={"title": "x"})
    assert r.status_code == 404


def test_update_task_no_valid_fields(client):
    created = client.post("/tasks", json={"title": "T"}).get_json()
    r = client.put(f"/tasks/{created['_id']}", json={"unknown_field": "value"})
    assert r.status_code == 400


#  DELETE /tasks/<id>

def test_delete_task(client):
    created = client.post("/tasks", json={"title": "Delete me"}).get_json()
    r = client.delete(f"/tasks/{created['_id']}")
    assert r.status_code == 200
    assert r.get_json()["message"] == "Task deleted successfully"


def test_delete_task_not_found(client):
    r = client.delete("/tasks/000000000000000000000000")
    assert r.status_code == 404


def test_delete_task_invalid_id(client):
    r = client.delete("/tasks/bad-id")
    assert r.status_code == 400
