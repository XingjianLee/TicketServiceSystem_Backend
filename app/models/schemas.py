from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

# 用户相关模型
class UserBase(BaseModel):
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    real_name: Optional[str] = None
    gender: Optional[str] = "未知"
    age: Optional[int] = None

class UserCreate(UserBase):
    password: str
    id_card: str

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    signature: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    real_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None

class UserResponse(UserBase):
    id: int
    avatar: Optional[str] = None
    signature: Optional[str] = None
    vip_level: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 认证相关模型
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# 航班相关模型
class FlightSearch(BaseModel):
    from_city: str
    to_city: str
    departure_date: str
    seat_class: Optional[str] = None

class FlightResponse(BaseModel):
    flight_id: int
    flight_number: str
    airline: str
    departure_city: str
    arrival_city: str
    departure_time: datetime
    arrival_time: datetime
    business_price: float
    economy_price: float
    first_class_price: float
    business_seats_available: int
    economy_seats_available: int
    first_class_seats_available: int
    status: str

# 订单相关模型
class PassengerInfo(BaseModel):
    passenger_name: str
    id_card: str
    phone: Optional[str] = None
    seat_class: str
    price: float

class OrderCreate(BaseModel):
    flight_id: int
    passengers: List[PassengerInfo]

class OrderResponse(BaseModel):
    order_id: int
    order_number: str
    total_price: float
    payment_status: str
    trip_status: str
    created_at: datetime
    passengers: List[PassengerInfo]

# 通用响应模型
class MessageResponse(BaseModel):
    message: str
    success: bool = True 