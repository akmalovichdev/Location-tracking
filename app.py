from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import time
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
# Настраиваем CORS для всех маршрутов
CORS(app, resources={r"/*": {"origins": "*"}})

# Путь к файлу для хранения данных
DATA_FILE = 'location_data.json'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@app.route('/api/update_location', methods=['POST', 'OPTIONS'])
def update_location():
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.json
    user_id = data.get('user_id')
    lat = data.get('latitude')
    lon = data.get('longitude')
    photo_url = data.get('photo_url')  # Получаем URL фото

    if not user_id or not lat or not lon:
        return jsonify({"error": "Missing data"}), 400

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    if user_id not in locations:
        locations[user_id] = []

    # Создаем запись с фото только если оно есть
    location_data = {
        "latitude": lat,
        "longitude": lon,
        "timestamp": timestamp
    }
    
    # Добавляем photo_url только если он не None
    if photo_url:
        location_data["photo_url"] = photo_url

    locations[user_id].append(location_data)

    # Сохраняем данные в файл
    save_data(locations)

    return jsonify({"message": "Location updated successfully!"})

@app.route('/api/get_locations', methods=['GET', 'OPTIONS'])
def get_locations():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify(locations)

@app.route('/api/get_user_history', methods=['GET', 'OPTIONS'])
def get_user_history():
    if request.method == 'OPTIONS':
        return '', 200
        
    user_id = request.args.get('user_id')
    if user_id in locations:
        return jsonify(locations[user_id])
    return jsonify({"error": "User not found"}), 404

@app.route('/api/delete_all_users', methods=['POST', 'OPTIONS'])
def delete_all_users():
    if request.method == 'OPTIONS':
        return '', 200
        
    global locations
    locations.clear()
    save_data(locations)  # Сохраняем пустые данные
    return jsonify({"message": "All users deleted successfully"})

@app.route('/api/upload_photo', methods=['POST', 'OPTIONS'])
def upload_photo():
    if request.method == 'OPTIONS':
        return '', 200

    if 'photo' not in request.files:
        return jsonify({"error": "No photo file"}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Добавляем timestamp к имени файла для уникальности
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({
            "message": "Photo uploaded successfully",
            "photo_url": f"/uploads/{filename}"
        })

    return jsonify({"error": "File type not allowed"}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=8888,
        debug=True
    ) 