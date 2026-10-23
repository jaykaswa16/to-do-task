import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Use a throwaway database so tests never touch the real tasks.db
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test_tasks.db")

import app as todo  # noqa: E402


def client():
    todo.init_db()
    return todo.app.test_client()


def test_home_page_loads():
    resp = client().get("/")
    assert resp.status_code == 200
    assert b"Task Manager" in resp.data


def test_add_task_appears_on_home_page():
    c = client()
    c.post("/add", data={"title": "Pipeline test task", "priority": "High"})
    resp = c.get("/")
    assert b"Pipeline test task" in resp.data


def test_toggle_unknown_task_returns_404():
    resp = client().post("/toggle/99999")
    assert resp.status_code == 404
