from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = ""
URL = "https://api.openweathermap.org/data/2.5/weather"


@app.route("/weather")
def weather():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "city required"}), 400

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    response = requests.get(URL, params=params)
    data = response.json()

    if response.status_code != 200:
        return jsonify({"error": data.get("message", "API error")}), 500

    return jsonify({
        "city": city,
        "temperature": data["main"]["temp"],
        "weather": data["weather"][0]["description"]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
