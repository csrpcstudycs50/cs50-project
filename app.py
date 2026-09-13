from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calibrate', methods=['POST'])
def calibrate():
    # Placeholder for calibration logic
    return jsonify({"message": "Calibration submitted!"})

@app.route('/measure', methods=['POST'])
def measure():
    # Placeholder for measurement logic
    return jsonify({"message": "Measurement submitted!"})

@app.route('/save', methods=['POST'])
def save():
    # Placeholder for save logic
    return jsonify({"message": "Measurements saved!"})


if __name__ == '__main__':
    app.run(debug=True)