from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# Модель для пользователя
class RegisterRequest(BaseModel):
    Email: EmailStr
    Password: str
    Username: str

# Модель для пользователя
class UserRequestModel(BaseModel):
    Username: str
    Email: str
    PasswordHash: str
    Role: Optional[str] = 'user'

# Модель для растения
class PlantRequestModel(BaseModel):
    UserID: int
    PlantName: str
    PlantType: str

# Модель для устройства
class DeviceRequestModel(BaseModel):
    UserID: int
    DeviceType: str
    Location: Optional[str] = None

# Модель для данных сенсоров
class SensorDataRequestModel(BaseModel):
    DeviceID: int
    SoilMoisture: float
    LightLevel: float
    Temperature: float
    Humidity: float
    Timestamp: Optional[datetime] = None

# Модель для уведомления
class NotificationRequestModel(BaseModel):
    UserID: int
    Message: str
    Status: Optional[str] = 'unread'

# Модель для настроек пользователя
class SettingRequestModel(BaseModel):
    UserID: int
    WateringSchedule: str
    LightPreferences: Optional[str] = None
    TemperatureRange: Optional[str] = None