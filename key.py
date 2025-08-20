from flask import Flask, request, jsonify
import json
import os
import random
import string
from datetime import datetime, timedelta

app = Flask(__name__)
DATA_FILE = "keys.json"


def load_keys():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_keys(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def generate_random_key():
    return "KEY-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


@app.route("/generate_key", methods=["POST"])
def generate_key():
    req = request.json
    user_id = req.get("user_id")

    if not user_id:
        return jsonify({"status": "error", "message": "Thiếu user_id"}), 400

    keys = load_keys()

    # tạo key mới
    new_key = generate_random_key()
    expiration_date = (datetime.now() + timedelta(days=1)).isoformat()

    keys[user_id] = {
        "key": new_key,
        "expiration": expiration_date
    }

    save_keys(keys)

    return jsonify({"status": "success", "user_id": user_id, "key": new_key, "expiration": expiration_date})


@app.route("/verify_key", methods=["POST"])
def verify_key():
    req = request.json
    user_id = req.get("user_id")
    key = req.get("key")

    if not user_id or not key:
        return jsonify({"status": "error", "message": "Thiếu user_id hoặc key"}), 400

    keys = load_keys()
    user_data = keys.get(user_id)

    if not user_data:
        return jsonify({"status": "error", "message": "Không tìm thấy user"}), 404

    if user_data["key"] != key:
        return jsonify({"status": "error", "message": "Key không hợp lệ"}), 401

    if datetime.fromisoformat(user_data["expiration"]) < datetime.now():
        return jsonify({"status": "error", "message": "Key đã hết hạn"}), 403

    return jsonify({"status": "success", "message": "Key hợp lệ"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
