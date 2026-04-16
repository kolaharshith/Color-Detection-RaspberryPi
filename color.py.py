from flask import Flask, jsonify, render_template
import board
import busio
import adafruit_tcs34725

app = Flask(__name__)

# Initialize I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize sensor
sensor = adafruit_tcs34725.TCS34725(i2c)

sensor.integration_time = 200
sensor.gain = 4

# RGB → HSV
def rgb_to_hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0

    max_val = max(r, g, b)
    min_val = min(r, g, b)
    delta = max_val - min_val

    # Hue
    if delta == 0:
        hue = 0
    elif max_val == r:
        hue = 60 * (((g - b) / delta) % 6)
    elif max_val == g:
        hue = 60 * (((b - r) / delta) + 2)
    else:
        hue = 60 * (((r - g) / delta) + 4)

    # Saturation
    sat = 0 if max_val == 0 else delta / max_val

    # Value
    val = max_val

    return hue, sat, val

# Detect color
def detect_color(r, g, b):
    hue, sat, val = rgb_to_hsv(r, g, b)

    if val < 0.1:
        return "black"
    elif sat < 0.2:
        if val > 0.8:
            return "white"
        else:
            return "gray"

    if hue < 15:
        return "red"
    elif hue < 45:
        return "orange"
    elif hue < 75:
        return "yellow"
    elif hue < 150:
        return "green"
    elif hue < 210:
        return "cyan"
    elif hue < 270:
        return "blue"
    elif hue < 330:
        return "purple"
    else:
        return "pink"

# Home page
@app.route('/')
def home():
    return render_template("index.html")

# API for color data
@app.route('/color')
def get_color():
    r, g, b = sensor.color_rgb_bytes
    color = detect_color(r, g, b)

    return jsonify({
        "r": r,
        "g": g,
        "b": b,
        "color": color
    })

# Run server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)