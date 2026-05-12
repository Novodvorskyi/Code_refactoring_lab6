from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
import os
from datetime import datetime

app = Flask(__name__)

# MongoDB connection
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.environ.get("DB_NAME", "taskdb")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
tasks_collection = db["tasks"]


def serialize_task(task):
    """Convert MongoDB document to JSON-serializable dict."""
    task["_id"] = str(task["_id"])
    return task


#  Health check

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})


# Tasks CRUD

@app.route("/tasks", methods=["GET"])
def get_tasks():
    """Return all tasks."""
    tasks = [serialize_task(t) for t in tasks_collection.find()]
    return jsonify(tasks), 200


@app.route("/tasks/<task_id>", methods=["GET"])
def get_task(task_id):
    """Return a single task by ID."""
    try:
        task = tasks_collection.find_one({"_id": ObjectId(task_id)})
    except InvalidId:
        return jsonify({"error": "Invalid ID format"}), 400

    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(serialize_task(task)), 200


@app.route("/tasks", methods=["POST"])
def create_task():
    """Create a new task."""
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "Field 'title' is required"}), 400

    task = {
        "title": data["title"],
        "description": data.get("description", ""),
        "done": False,
        "created_at": datetime.utcnow().isoformat(),
    }
    result = tasks_collection.insert_one(task)
    task["_id"] = str(result.inserted_id)
    return jsonify(task), 201


@app.route("/tasks/<task_id>", methods=["PUT"])
def update_task(task_id):
    """Update an existing task."""
    try:
        oid = ObjectId(task_id)
    except InvalidId:
        return jsonify({"error": "Invalid ID format"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    allowed = {"title", "description", "done"}
    update_fields = {k: v for k, v in data.items() if k in allowed}
    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    result = tasks_collection.update_one({"_id": oid}, {"$set": update_fields})
    if result.matched_count == 0:
        return jsonify({"error": "Task not found"}), 404

    updated = tasks_collection.find_one({"_id": oid})
    return jsonify(serialize_task(updated)), 200


@app.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete a task."""
    try:
        oid = ObjectId(task_id)
    except InvalidId:
        return jsonify({"error": "Invalid ID format"}), 400

    result = tasks_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({"message": "Task deleted successfully"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
