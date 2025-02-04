from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Plant, Device, SensorData, Notification, Setting
from datetime import timedelta

# Ініціалізація Flask-додатку
app = Flask(__name__)

# Налаштування бази даних і JWT
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:31415926@localhost/smart_plant_care'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'my_very_secret_key_12345'  # Змініть на секретний ключ
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Ініціалізація бази даних та JWT
db.init_app(app)
jwt = JWTManager(app)

@app.route('/')
def home():
    return "Добро пожаловать на главную страницу!"

# Реєстрація нового користувача
@app.route('/auth/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({"msg": "Missing required fields"}), 400
    
    hashed_password = generate_password_hash(password, method='sha256')
    
    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"msg": "User created successfully"}), 201

# Аутентифікація користувача
@app.route('/auth/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"msg": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200

# Отримання інформації про поточного користувача
@app.route('/users/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    return jsonify({
        "username": user.username,
        "email": user.email
    }), 200

# Оновлення профілю користувача
@app.route('/users/me', methods=['PUT'])
@jwt_required()
def update_user_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    data = request.get_json()
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    
    db.session.commit()
    return jsonify({"msg": "User profile updated successfully"}), 200

# Додавання нової рослини
@app.route('/plants/', methods=['POST'])
@jwt_required()
def add_plant():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    plant_name = data.get('plant_name')
    plant_type = data.get('plant_type')
    
    if not plant_name or not plant_type:
        return jsonify({"msg": "Missing required fields"}), 400
    
    new_plant = Plant(user_id=current_user_id, plant_name=plant_name, plant_type=plant_type)
    db.session.add(new_plant)
    db.session.commit()
    
    return jsonify({"msg": "Plant added successfully"}), 201

# Отримання списку рослин користувача
@app.route('/plants/', methods=['GET'])
@jwt_required()
def get_plants():
    current_user_id = get_jwt_identity()
    plants = Plant.query.filter_by(user_id=current_user_id).all()
    
    if not plants:
        return jsonify({"msg": "No plants found for this user"}), 404
    
    plant_list = []
    for plant in plants:
        plant_list.append({
            "plant_id": plant.id,
            "plant_name": plant.plant_name,
            "plant_type": plant.plant_type
        })
    
    return jsonify(plant_list), 200

# Отримання даних сенсора для рослини
@app.route('/plants/<int:plant_id>/sensor_data', methods=['GET'])
@jwt_required()
def get_sensor_data(plant_id):
    current_user_id = get_jwt_identity()
    plant = Plant.query.get(plant_id)
    
    if not plant or plant.user_id != current_user_id:
        return jsonify({"msg": "Plant not found or unauthorized access"}), 404
    
    sensor_data = SensorData.query.filter_by(plant_id=plant_id).all()
    
    if not sensor_data:
        return jsonify({"msg": "No sensor data available for this plant"}), 404
    
    data = []
    for sensor in sensor_data:
        data.append({
            "timestamp": sensor.timestamp,
            "temperature": sensor.temperature,
            "humidity": sensor.humidity,
            "moisture": sensor.moisture
        })
    
    return jsonify(data), 200

# Оновлення налаштувань рослини (наприклад, полив або освітлення)
@app.route('/plants/<int:plant_id>/settings', methods=['PUT'])
@jwt_required()
def update_plant_settings(plant_id):
    current_user_id = get_jwt_identity()
    plant = Plant.query.get(plant_id)
    
    if not plant or plant.user_id != current_user_id:
        return jsonify({"msg": "Plant not found or unauthorized access"}), 404
    
    data = request.get_json()
    watering_schedule = data.get('watering_schedule')
    lighting_schedule = data.get('lighting_schedule')
    
    if watering_schedule:
        plant.watering_schedule = watering_schedule
    if lighting_schedule:
        plant.lighting_schedule = lighting_schedule
    
    db.session.commit()
    
    return jsonify({"msg": "Plant settings updated successfully"}), 200

# Створення сповіщень (наприклад, нагадування про полив або освітлення)
@app.route('/notifications', methods=['POST'])
@jwt_required()
def create_notification():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    notification_type = data.get('notification_type')
    content = data.get('content')
    
    if not notification_type or not content:
        return jsonify({"msg": "Missing required fields"}), 400
    
    new_notification = Notification(user_id=current_user_id, notification_type=notification_type, content=content)
    db.session.add(new_notification)
    db.session.commit()
    
    return jsonify({"msg": "Notification created successfully"}), 201

# Основна функція запуску додатку
if __name__ == '__main__':
    app.run(debug=True)
