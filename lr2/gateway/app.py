from flask import Flask, request, jsonify
import requests
from multiprocessing import Process, Queue
import os

app = Flask(__name__)

WEATHER_URL = os.getenv("WEATHER_URL", "http://localhost:5000/weather")
RECOMMEND_URL = os.getenv("RECOMMEND_URL", "http://localhost:5001/recommend")
HISTORY_URL = os.getenv("HISTORY_URL", "http://localhost:5002/history")


def get_weather(city, queue):
    response = requests.get(WEATHER_URL, params={"city": city})
    queue.put(response.json())


def save_history(city):
    requests.post(HISTORY_URL, json={"city": city})


@app.route("/full-weather")
def full_weather():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "city required"}), 400

    queue = Queue()

    # Получаем погоду и сохраняем историю
    p1 = Process(target=get_weather, args=(city, queue))
    p2 = Process(target=save_history, args=(city,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    weather = queue.get()

    # Получаем рекомендации
    recommendations = requests.post(
        RECOMMEND_URL,
        json=weather
    ).json()

    return jsonify({
        "Погода": weather,
        "Рекомендации": recommendations["recommendations"]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
