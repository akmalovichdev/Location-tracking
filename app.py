from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import time
import json
import os

app = Flask(__name__)
CORS(app)

# Путь к файлу для хранения данных
DATA_FILE = 'location_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Загружаем данные при запуске
locations = load_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/update_location', methods=['POST'])
def update_location():
    data = request.json
    user_id = data.get('user_id')
    lat = data.get('latitude')
    lon = data.get('longitude')

    if not user_id or not lat or not lon:
        return jsonify({"error": "Missing data"}), 400

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    if user_id not in locations:
        locations[user_id] = []

    locations[user_id].append({
        "latitude": lat,
        "longitude": lon,
        "timestamp": timestamp
    })

    # Сохраняем данные в файл
    save_data(locations)

    return jsonify({"message": "Location updated successfully!"})

@app.route('/api/get_locations', methods=['GET'])
def get_locations():
    return jsonify(locations)

@app.route('/api/get_user_history', methods=['GET'])
def get_user_history():
    user_id = request.args.get('user_id')
    if user_id in locations:
        return jsonify(locations[user_id])
    return jsonify({"error": "User not found"}), 404

@app.route('/api/delete_all_users', methods=['POST'])
def delete_all_users():
    global locations
    locations.clear()
    save_data(locations)  # Сохраняем пустые данные
    return jsonify({"message": "All users deleted successfully"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True) 