import os
import sqlite3
from flask import Flask, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

DB_PATH = os.getenv("DB_PATH", "/data/tasks.db")

def connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        done INTEGER NOT NULL DEFAULT 0
    )""")
    db.commit()
    return db

@app.get("/api/health")
def health():
    return jsonify(status="ok", service="task-manager-api")

@app.get("/api/tasks")
def list_tasks():
    with connect() as db:
        rows = db.execute("SELECT id, title, done FROM tasks ORDER BY id DESC").fetchall()
    return jsonify([{"id": r["id"], "title": r["title"], "done": bool(r["done"])} for r in rows])

@app.post("/api/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    if not title:
        return jsonify(error="Название задачи обязательно"), 400
    with connect() as db:
        cur = db.execute("INSERT INTO tasks(title) VALUES (?)", (title,))
        task_id = cur.lastrowid
    return jsonify(id=task_id, title=title, done=False), 201

@app.patch("/api/tasks/<int:task_id>")
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    with connect() as db:
        row = db.execute("SELECT id, title, done FROM tasks WHERE id=?", (task_id,)).fetchone()
        if row is None:
            return jsonify(error="Задача не найдена"), 404
        done = bool(data.get("done", not bool(row["done"])))
        db.execute("UPDATE tasks SET done=? WHERE id=?", (int(done), task_id))
    return jsonify(id=task_id, title=row["title"], done=done)

@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    with connect() as db:
        cur = db.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        if cur.rowcount == 0:
            return jsonify(error="Задача не найдена"), 404
    return jsonify(deleted=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
