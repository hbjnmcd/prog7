from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    recommendations = []

    if "дождь" in data["weather"]:
        recommendations.append("Возьмите зонт ☔")

    if data["temperature"] < 5:
        recommendations.append("Одевайтесь теплее 🧥")
    elif data["temperature"] > 25:
        recommendations.append("Очень жарко, не забудьте водичку 💧")
    else:
        recommendations.append("Температура комфортная")

    return jsonify({"recommendations": recommendations})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
