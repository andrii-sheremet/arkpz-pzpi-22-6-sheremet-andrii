from flask_sqlalchemy import SQLAlchemy

# Ініціалізація SQLAlchemy
db = SQLAlchemy()

# Модель користувача
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    # Визначення зв'язків
    plants = db.relationship('Plant', backref='owner', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

# Модель рослини
class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Визначення зв'язків
    devices = db.relationship('Device', backref='plant', lazy=True)
    
    def __repr__(self):
        return f'<Plant {self.name}>'

# Модель пристрою
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    plant_id = db.Column(db.Integer, db.ForeignKey('plant.id'), nullable=False)
    
    # Визначення зв'язків
    sensor_data = db.relationship('SensorData', backref='device', lazy=True)
    
    def __repr__(self):
        return f'<Device {self.name}>'

# Модель даних сенсора
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    
    def __repr__(self):
        return f'<SensorData {self.value} at {self.timestamp}>'

# Модель повідомлення
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return f'<Notification {self.message}>'

# Модель налаштувань
class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    value = db.Column(db.String(120), nullable=False)
    
    def __repr__(self):
        return f'<Setting {self.name}: {self.value}>'

