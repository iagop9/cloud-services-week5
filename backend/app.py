from flask import Flask, jsonify
import os
import mysql.connector
import requests

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "db")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.getenv("DB_NAME", "appdb")


def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


@app.get("/api/health")
def health():
    return jsonify(status="ok")


@app.get("/api")
def index():
    conn = get_connection()
    cur = conn.cursor()

    # Persistent write
    cur.execute("UPDATE visits SET count = count + 1 WHERE id = 1")
    conn.commit()

    # Read persistent counter and MySQL server time
    cur.execute("SELECT count, NOW() FROM visits WHERE id = 1")
    row = cur.fetchone()

    cur.close()
    conn.close()

    return jsonify(
        message="Hello from MySQL via Flask!",
        visits=row[0],
        database_time=str(row[1])
    )


@app.get("/api/weather")
def weather():
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": 65.0121,
        "longitude": 25.4651,
        "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m",
        "wind_speed_unit": "kmh",
        "timezone": "Europe/Helsinki"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        current = data["current"]

        return jsonify(
            location="Oulu, Finland",
            temperature=current["temperature_2m"],
            apparent_temperature=current["apparent_temperature"],
            wind_speed=current["wind_speed_10m"],
            weather_code=current["weather_code"],
            time=current["time"]
        )

    except requests.RequestException as error:
        return jsonify(
            error="Could not retrieve weather data",
            details=str(error)
        ), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
