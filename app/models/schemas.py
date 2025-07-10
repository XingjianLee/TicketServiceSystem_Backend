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
    company: Optional[str] = None
    user_type: str = "passenger"  # passenger 或 agency

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    signature: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    real_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    company: Optional[str] = None

class UserResponse(UserBase):
    id: int
    avatar: Optional[str] = None
    signature: Optional[str] = None
    vip_level: int
    company: Optional[str] = None
    user_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# 认证相关模型
class UserLogin(BaseModel):
    email: str  # 前端使用email登录
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    username: Optional[str] = None

# 航班相关模型
class FlightSearch(BaseModel):
    from_city: str
    to_city: str
    departure_date: str
    return_date: Optional[str] = None
    passengers: int = 1
    seat_class: Optional[str] = None
    trip_type: str = "oneWay"  # oneWay 或 roundTrip

class FlightResponse(BaseModel):
    id: int
    airline: str
    flight_number: str
    departure: dict  # {city: str, time: str, airport: str}
    arrival: dict    # {city: str, time: str, airport: str}
    duration: str
    price: float
    class_type: str
    seats_available: int
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
    id: str
    flight_number: str
    route: str
    date: str
    time: str
    passengers: int
    class_type: str
    price: float
    status: str
    booking_date: str
    seat_number: Optional[str] = None
    order_id: int
    order_number: str
    total_price: float
    payment_status: str
    trip_status: str
    created_at: datetime

# 选座相关模型
class SeatSelect(BaseModel):
    order_id: int
    seat_number: str

class SeatResponse(BaseModel):
    seat_number: str
    available: bool

# 通知相关模型
class Notice(BaseModel):
    id: int
    title: str
    content: str
    type: str  # info, warning, success, error
    created_at: datetime
    is_read: bool = False

class NoticeCreate(BaseModel):
    title: str
    content: str
    type: str = "info"

# 通用响应模型
class MessageResponse(BaseModel):
    message: str
    success: bool = True

# 统计相关模型
class UserStats(BaseModel):
    total_flights: int
    visited_cities: int
    total_miles: float
    vip_level: int
    points: int 