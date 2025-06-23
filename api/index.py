
from flask import Flask, request, render_template, redirect, url_for
import hashlib
import requests

app = Flask(__name__)

def md5_hash(password):
    return hashlib.md5(password.encode()).hexdigest()

def parse_device_data(device_data_str):
    bytes_list = [int(b, 16) if len(b) > 1 else int(b, 16) for b in device_data_str.split('-')]
    def get_word(index):
        return bytes_list[index] + (bytes_list[index + 1] << 8)
    parsed_data = {
        "ac_input_voltage": round(get_word(5) * 0.1, 1),
        "ac_input_frequency": round(get_word(7) * 0.1, 1),
        "battery_voltage": round(get_word(13) * 0.1, 1),
        "battery_capacity_percent": bytes_list[15],
        "output_voltage": round(get_word(21) * 0.1, 1),
        "output_frequency": round(get_word(23) * 0.1, 1),
        "working_mode": "Invert mode",  # Hardcoded for now
        "output_load_percent": bytes_list[61]  # Aproximado
    }
    return parsed_data

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = md5_hash(request.form["password"])
        try:
            r = requests.post("https://proxy-login-avenzo.onrender.com/auth/login", json={
                "username": username,
                "password": password
            })
            r.raise_for_status()
            res = r.json()
            device_data = res["data"]["bindDeviceList"][0]["deviceData"]
            parsed = parse_device_data(device_data)
            return render_template("dashboard.html", data=parsed)
        except Exception as e:
            return f"Error: {str(e)}"
    return render_template("login.html")

def handler(environ, start_response):
    return app(environ, start_response)
