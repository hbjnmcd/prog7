from flask import Flask, request, jsonify
from collections import Counter

app = Flask(__name__)
history = []

@app.route("/history", methods=["POST"])
def save():
    city = request.json["city"]
    history.append(city)
    return jsonify({"status": "saved"})

@app.route("/history", methods=["GET"])
def stats():
    return jsonify(dict(Counter(history)))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
