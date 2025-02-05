from __future__ import annotations

from os import urandom

from sqlalchemy import Column, Integer, Boolean, Numeric, String, ForeignKey, Float, func, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

ModelsBase = declarative_base()


def gen_device_api_key() -> str:
    return urandom(16).hex()

# Модель пользователя
class User(ModelsBase):
    __tablename__ = 'Users'

    UserId: int = Column(Integer, primary_key=True, autoincrement=True)
    Username: str = Column(String(50), nullable=False)
    Email: str = Column(String(255), nullable=False, unique=True)
    PasswordHash: str = Column(String(64), nullable=False)
    Role: str = Column(String(10), nullable=False, default='user')

    def to_json(self) -> dict:
        return {
            "id": self.UserId,
            "username": self.Username,
            "email": self.Email,
            "Role": self.Role
        }

# Модель растения
class Plant(ModelsBase):
    __tablename__ = 'Plants'

    PlantID: int = Column(Integer, primary_key=True, autoincrement=True)
    UserID: int = Column(Integer, ForeignKey('Users.UserId'), nullable=False)
    PlantName: str = Column(String(50), nullable=False)
    PlantType: str = Column(String(50), nullable=False)
    AddedDate = Column(DateTime, default=func.current_timestamp())

    # Связь с пользователем
    user = relationship('User', backref='plants', lazy=True)

    def to_json(self) -> dict:
        return {
            "id": self.PlantID,
            "user_id": self.UserID,
            "plant_name": self.PlantName,
            "plant_type": self.PlantType,
            "added_date": self.AddedDate
        }

# Модель устройства
class Device(ModelsBase):
    __tablename__ = 'Devices'

    DeviceID: int = Column(Integer, primary_key=True, autoincrement=True)
    UserID: int = Column(Integer, ForeignKey('Users.UserId'), nullable=False)
    DeviceType: str = Column(String(10), nullable=False)
    Location: str = Column(String(100))

    # Связь с данными сенсоров
    sensor_data_id: int = Column(Integer, ForeignKey('SensorData.SensorDataID'), nullable=False)

    # Связь с SensorData
    sensor_data = relationship('SensorData', backref='devices', lazy=True)

    def to_json(self) -> dict:
        return {
            "id": self.DeviceID,
            "user_id": self.UserID,
            "device_type": self.DeviceType,
            "location": self.Location,
            "sensor_data_id": self.sensor_data_id
        }

# Модель данных сенсоров
class SensorData(ModelsBase):
    __tablename__ = 'SensorData'

    DataID: int = Column(Integer, primary_key=True, autoincrement=True)
    DeviceID: int = Column(Integer, ForeignKey('Devices.DeviceID'), nullable=False)
    Timestamp: str = Column(DateTime, default=func.current_timestamp())
    SoilMoisture: float = Column(Numeric(5, 2), nullable=False)
    LightLevel: float = Column(Numeric(5, 2), nullable=False)
    Temperature: float = Column(Numeric(5, 2), nullable=False)
    Humidity: float = Column(Numeric(5, 2), nullable=False)

    def to_json(self) -> dict:
        return {
            "id": self.DataID,
            "device_id": self.DeviceID,
            "timestamp": self.Timestamp,
            "soil_moisture": float(self.SoilMoisture),
            "light_level": float(self.LightLevel),
            "temperature": float(self.Temperature),
            "humidity": float(self.Humidity)
        }

# Модель уведомлений
class Notification(ModelsBase):
    __tablename__ = 'Notifications'

    NotificationID: int = Column(Integer, primary_key=True, autoincrement=True)
    UserID: int = Column(Integer, ForeignKey('Users.UserID'), nullable=False)
    Message: str = Column(String(255), nullable=False)
    CreatedDate: str = Column(DateTime, default=func.current_timestamp())
    Status: str = Column(String(10), default='unread')

    def to_json(self) -> dict:
        return {
            "id": self.NotificationID,
            "user_id": self.UserID,
            "message": self.Message,
            "created_date": self.CreatedDate,
            "status": self.Status
        }

# Модель настроек
class Setting(ModelsBase):
    __tablename__ = 'Settings'

    SettingID: int = Column(Integer, primary_key=True, autoincrement=True)
    UserID: int = Column(Integer, ForeignKey('Users.UserID'), nullable=False)
    WateringSchedule: str = Column(String(255), nullable=False)
    LightPreferences: str = Column(String(255))
    TemperatureRange: str = Column(String(50))

    def to_json(self) -> dict:
        return {
            "id": self.SettingID,
            "user_id": self.UserID,
            "watering_schedule": self.WateringSchedule,
            "light_preferences": self.LightPreferences,
            "temperature_range": self.TemperatureRange
        }