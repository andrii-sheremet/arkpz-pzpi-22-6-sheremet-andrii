import json
import ssl
from datetime import datetime
from time import time, UTC

import bcrypt
from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy
import jwt
from flask_mqtt import Mqtt
from flask_openapi3 import OpenAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from errors import NotAuthorizedError
from models import User, Plant, Device, SensorData, Notification, Setting
from request_models import UserRequestModel, RegisterRequest, PlantRequestModel, DeviceRequestModel, SensorDataRequestModel, NotificationRequestModel, SettingRequestModel

app = OpenAPI(__name__, doc_prefix="/docs")
JWT_EXPIRE_TIME = 60 * 60 * 24
JWT_KEY = b"0123456789abcdef"

app.config['SECRET_KEY'] = 'your_secret_key'

app.config["MQTT_BROKER_URL"] = "localhost"
app.config["MQTT_BROKER_PORT"] = 1883
app.config["MQTT_USERNAME"] = ""
app.config["MQTT_PASSWORD"] = "" 
app.config["MQTT_KEEPALIVE"] = 60
app.config["MQTT_TLS_ENABLED"] = False
app.config["MQTT_TLS_INSECURE"] = False

mqtt = Mqtt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:31415926@localhost/smart_plant_care'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@mqtt.on_connect()
def handle_mqtt_connect(client, userdata, flags, rc):
    mqtt.subscribe("smart_plant_care")

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    try:
        payload = json.loads(message.payload)
    except ValueError:
        return

    if message.topic != "smart_plant_care":
        return

    if "enabled" not in payload or "enabled_for" not in payload or "token" not in payload:
        return

    if not isinstance(payload["enabled"], bool) or not isinstance(payload["enabled_for"], (int, type(None))):
        return

@app.errorhandler(NotAuthorizedError)
def handle_not_authorized(_):
    return {"error": "Not authorized!"}, 401

def auth_user(token: str) -> User:
    token = jwt.decode(token, JWT_KEY, algorithms=["HS256"])
    user = db.session.query(User).filter_by(id=token["user"]).scalar()
    if user is None:
        raise NotAuthorizedError

    return user


def auth_admin(token: str) -> User:
    user = auth_user(token)
    if not user.Role == "admin":
        raise NotAuthorizedError

    return user


@app.post("/auth/register")
def register(body: RegisterRequest):
    if db.session.query(User).filter_by(Email=body.email).scalar() is not None:
        return {"error": "User with this email already exists!"}, 400

    password_hash = bcrypt.hashpw(body.password.encode("utf8"), bcrypt.gensalt()).decode("utf8")
    user = User(Username=body.Username, Email=body.Email, PasswordHash=body.Password)
    db.session.add(user)
    db.session.commit()

    return {
        "token": jwt.encode({
            "user": user.id,
            "exp": int(time() + JWT_EXPIRE_TIME)
        }, JWT_KEY)
    }

@app.post("/auth/login")
def login(body: RegisterRequest):
    user = db.session.query(User).filter_by(Email=body.Email).scalar()
    if user is None:
        return {"error": "User with this credentials does not exist!"}, 400

    if not bcrypt.checkpw(body.Password.encode("utf8"), user.PasswordHash.encode("utf8")):
        return {"error": "User with this credentials does not exist!"}, 400

    return {
        "token": jwt.encode({
            "user": user.id,
            "exp": int(time() + JWT_EXPIRE_TIME)
        }, JWT_KEY, algorithm="HS256")
    }

# Получение информации о текущем пользователе
@app.route('/users/me', methods=['GET'])
def get_user(current_user):
    user_data = UserRequestModel.from_orm(current_user)
    return jsonify(user_data.dict())

# Обновление информации о пользователе
@app.route('/users/me', methods=['PUT'])
def update_user(current_user):
    data = request.get_json()
    try:
        user_data = UserRequestModel(**data)  # Validate incoming data
    except Exception as e:
        return jsonify({'message': str(e)}), 400
    
    current_user.Email = user_data.Email
    current_user.Username = user_data.Username
    if user_data.PasswordHash:
        current_user.PasswordHash = user_data.PasswordHash
    
    db.session.commit()
    return jsonify({'message': 'User profile updated successfully!'})

# Добавление нового растения
@app.route('/plants/', methods=['POST'])
def add_plant(current_user):
    data = request.get_json()
    try:
        plant_data = PlantRequestModel(**data)  # Validate incoming data
    except Exception as e:
        return jsonify({'message': str(e)}), 400
    
    new_plant = Plant(UserID=current_user.id, PlantName=plant_data.PlantName, PlantType=plant_data.PlantType)
    db.session.add(new_plant)
    db.session.commit()
    return jsonify({'message': 'Plant added successfully!'}), 201

# Получение списка растений
@app.route('/plants/', methods=['GET'])
def get_plants(current_user):
    plants = Plant.query.filter_by(UserID=current_user.id).all()
    plants_data = [PlantRequestModel.from_orm(plant).dict() for plant in plants]
    return jsonify(plants_data)

# Получение информации о растении
@app.route('/plants/<int:plant_id>', methods=['GET'])
def get_plant(current_user, plant_id):
    plant = Plant.query.filter_by(UserID=current_user.id, id=plant_id).first()
    if not plant:
        return jsonify({'message': 'Plant not found!'}), 404
    plant_data = PlantRequestModel.from_orm(plant)
    return jsonify(plant_data.dict())

# Обновление информации о растении
@app.route('/plants/<int:plant_id>', methods=['PUT'])
def update_plant(current_user, plant_id):
    data = request.get_json()
    try:
        plant_data = PlantRequestModel(**data)  # Validate incoming data
    except Exception as e:
        return jsonify({'message': str(e)}), 400
    
    plant = Plant.query.filter_by(UserID=current_user.id, id=plant_id).first()
    if not plant:
        return jsonify({'message': 'Plant not found!'}), 404

    plant.PlantName = plant_data.PlantName
    plant.PlantType = plant_data.PlantType
    db.session.commit()
    return jsonify({'message': 'Plant updated successfully!'})

# Удаление растения
@app.route('/plants/<int:plant_id>', methods=['DELETE'])
def delete_plant(current_user, plant_id):
    plant = Plant.query.filter_by(UserID=current_user.id, id=plant_id).first()
    if not plant:
        return jsonify({'message': 'Plant not found!'}), 404
    
    db.session.delete(plant)
    db.session.commit()
    return jsonify({'message': 'Plant deleted successfully!'})

# Добавление нового устройства
@app.route('/devices/', methods=['POST'])
def add_device(current_user):
    data = request.get_json()
    try:
        device_data = DeviceRequestModel(**data)  # Validate incoming data
    except Exception as e:
        return jsonify({'message': str(e)}), 400
    
    new_device = Device(UserID=current_user.id, DeviceType=device_data.DeviceType, Location=device_data.Location)
    db.session.add(new_device)
    db.session.commit()
    return jsonify({'message': 'Device added successfully!'}), 201

# Получение списка устройств
@app.route('/devices/', methods=['GET'])
def get_devices(current_user):
    devices = Device.query.filter_by(UserID=current_user.id).all()
    devices_data = [DeviceRequestModel.from_orm(device).dict() for device in devices]
    return jsonify(devices_data)

# Получение информации о устройстве
@app.route('/devices/<int:device_id>', methods=['GET'])
def get_device(current_user, device_id):
    device = Device.query.filter_by(UserID=current_user.id, id=device_id).first()
    if not device:
        return jsonify({'message': 'Device not found!'}), 404
    device_data = DeviceRequestModel.from_orm(device)
    return jsonify(device_data.dict())

# Удаление устройства
@app.route('/devices/<int:device_id>', methods=['DELETE'])
def delete_device(current_user, device_id):
    device = Device.query.filter_by(UserID=current_user.id, id=device_id).first()
    if not device:
        return jsonify({'message': 'Device not found!'}), 404
    
    db.session.delete(device)
    db.session.commit()
    return jsonify({'message': 'Device deleted successfully!'})

# Получение последних показателей сенсора
@app.route('/sensors/data/<int:device_id>', methods=['GET'])
def get_sensor_data(current_user, device_id):
    sensor_data = SensorData.query.filter_by(DeviceID=device_id).order_by(SensorData.Timestamp.desc()).first()
    if not sensor_data:
        return jsonify({'message': 'No data found!'}), 404
    sensor_data_response = SensorDataRequestModel.from_orm(sensor_data)
    return jsonify(sensor_data_response.dict())

# Отправка данных с сенсоров
@app.route('/sensors/data', methods=['POST'])
def post_sensor_data(current_user):
    data = request.get_json()
    try:
        sensor_data = SensorDataRequestModel(**data)  # Validate incoming data
    except Exception as e:
        return jsonify({'message': str(e)}), 400
    
    new_sensor_data = SensorData(
        DeviceID=sensor_data.DeviceID,
        SoilMoisture=sensor_data.SoilMoisture,
        LightLevel=sensor_data.LightLevel,
        Temperature=sensor_data.Temperature,
        Humidity=sensor_data.Humidity,
        Timestamp=datetime.utcnow()
    )
    db.session.add(new_sensor_data)
    db.session.commit()
    return jsonify({'message': 'Sensor data added successfully!'}), 201

# Получение уведомлений
@app.route('/notifications/', methods=['GET'])
def get_notifications(current_user):
    notifications = Notification.query.filter_by(UserID=current_user.id).all()
    notifications_data = [NotificationRequestModel.from_orm(notification).dict() for notification in notifications]
    return jsonify(notifications_data)

# Обновление статуса уведомления
@app.route('/notifications/<int:notification_id>', methods=['PUT'])
def mark_notification_read(current_user, notification_id):
    notification = Notification.query.filter_by(UserID=current_user.id, id=notification_id).first()
    if not notification:
        return jsonify({'message': 'Notification not found!'}), 404
    
    notification.Status = 'read'
    db.session.commit()
    return jsonify({'message': 'Notification marked as read!'})

# Получение настроек пользователя
@app.route('/settings/', methods=['GET'])
def get_settings(current_user):
    settings = Setting.query.filter_by(UserID=current_user.id).first()
    if not settings:
        return jsonify({'message': 'Settings not found!'}), 404
    settings_data = SettingRequestModel.from_orm(settings)
    return jsonify(settings_data.dict())

# Обновление настроек пользователя
@app.route('/settings/', methods=['PUT'])
def update_settings(current_user):
    data = request.get_json()
    try:
        settings_data = SettingRequestModel(**data)  # Validate incoming data
    except Exception as e:
        return jsonify({'message': str(e)}), 400
    
    settings = Setting.query.filter_by(UserID=current_user.id).first()
    if not settings:
        return jsonify({'message': 'Settings not found!'}), 404
    
    settings.WateringSchedule = settings_data.WateringSchedule
    settings.LightPreferences = settings_data.LightPreferences
    settings.TemperatureRange = settings_data.TemperatureRange
    db.session.commit()
    return jsonify({'message': 'Settings updated successfully!'})

if __name__ == '__main__':
    app.run(debug=True)
