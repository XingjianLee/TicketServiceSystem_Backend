# -*- coding: utf-8 -*-
# @Author  : Xingjian Li
# @Time    : 2025/7/11 下午8:32
# @File    : models.py
# @Software: PyCharm

from typing import List, Dict, Any, Optional
from datetime import datetime
from .database import get_database

db = get_database()


class BaseModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建实例"""
        return cls(**data)


class User(BaseModel):
    """用户模型"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = kwargs.get('id')
        self.username = kwargs.get('username')
        self.nickname = kwargs.get('nickname')
        self.avatar = kwargs.get('avatar')
        self.signature = kwargs.get('signature')
        self.password = kwargs.get('password')
        self.email = kwargs.get('email')
        self.phone = kwargs.get('phone')
        self.id_card = kwargs.get('id_card')
        self.real_name = kwargs.get('real_name')
        self.gender = kwargs.get('gender', '未知')
        self.age = kwargs.get('age')
        self.user_type = kwargs.get('user_type', 'passenger')
        self.vip_level = kwargs.get('vip_level', 0)
        self.created_at = kwargs.get('created_at')
    
    @classmethod
    def get_by_id(cls, user_id: int) -> Optional['User']:
        """根据ID获取用户"""
        data = db.get_by_id('users', user_id)
        return cls(**data) if data else None
    
    @classmethod
    def get_by_username(cls, username: str) -> Optional['User']:
        """根据用户名获取用户"""
        data = db.execute_one("SELECT * FROM users WHERE username = %s", (username,))
        return cls(**data) if data else None
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional['User']:
        """根据邮箱获取用户"""
        data = db.execute_one("SELECT * FROM users WHERE email = %s", (email,))
        return cls(**data) if data else None
    
    @classmethod
    def get_by_phone(cls, phone: str) -> Optional['User']:
        """根据手机号获取用户"""
        data = db.execute_one("SELECT * FROM users WHERE phone = %s", (phone,))
        return cls(**data) if data else None
    
    @classmethod
    def get_by_id_card(cls, id_card: str) -> Optional['User']:
        """根据身份证号获取用户"""
        data = db.execute_one("SELECT * FROM users WHERE id_card = %s", (id_card,))
        return cls(**data) if data else None
    
    @classmethod
    def get_all(cls, skip: int = 0, limit: int = 100) -> List['User']:
        """获取所有用户"""
        query = "SELECT * FROM users ORDER BY created_at DESC LIMIT %s OFFSET %s"
        data_list = db.execute_query(query, (limit, skip))
        return [cls(**data) for data in data_list]
    
    @classmethod
    def delete_by_id(cls, user_id: int) -> bool:
        """根据ID删除用户"""
        result = db.execute_update("DELETE FROM users WHERE id = %s", (user_id,))
        return result > 0
    
    def save(self) -> int:
        """保存用户"""
        if self.id:
            # 更新
            data = self.to_dict()
            data.pop('id', None)  # 移除id字段
            data.pop('created_at', None)  # 移除创建时间
            return db.update('users', data, 'id = %s', (self.id,))
        else:
            # 插入
            data = self.to_dict()
            data.pop('id', None)  # 移除id字段
            self.id = db.insert('users', data)
            return self.id


class Aircraft(BaseModel):
    """飞机型号模型"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.aircraft_id = kwargs.get('aircraft_id')
        self.model_name = kwargs.get('model_name')
        self.business_capacity = kwargs.get('business_capacity', 0)
        self.first_class_capacity = kwargs.get('first_class_capacity', 0)
        self.economy_capacity = kwargs.get('economy_capacity', 0)
    
    @classmethod
    def get_by_id(cls, aircraft_id: int) -> Optional['Aircraft']:
        """根据ID获取飞机型号"""
        data = db.get_by_id('aircraft', aircraft_id, 'aircraft_id')
        return cls(**data) if data else None
    
    @classmethod
    def get_all(cls) -> List['Aircraft']:
        """获取所有飞机型号"""
        data_list = db.get_all('aircraft')
        return [cls(**data) for data in data_list]


class Route(BaseModel):
    """航线模型"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.route_id = kwargs.get('route_id')
        self.departure_city = kwargs.get('departure_city')
        self.arrival_city = kwargs.get('arrival_city')
        self.distance_km = kwargs.get('distance_km')
    
    @classmethod
    def get_by_id(cls, route_id: int) -> Optional['Route']:
        """根据ID获取航线"""
        data = db.get_by_id('routes', route_id, 'route_id')
        return cls(**data) if data else None
    
    @classmethod
    def get_by_cities(cls, departure_city: str, arrival_city: str) -> Optional['Route']:
        """根据出发和到达城市获取航线"""
        data = db.execute_one(
            "SELECT * FROM routes WHERE departure_city = %s AND arrival_city = %s",
            (departure_city, arrival_city)
        )
        return cls(**data) if data else None
    
    @classmethod
    def get_all(cls) -> List['Route']:
        """获取所有航线"""
        data_list = db.get_all('routes')
        return [cls(**data) for data in data_list]


class Flight(BaseModel):
    """航班模型"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.flight_id = kwargs.get('flight_id')
        self.flight_number = kwargs.get('flight_number')
        self.airline = kwargs.get('airline')
        self.route_id = kwargs.get('route_id')
        self.aircraft_id = kwargs.get('aircraft_id')
        self.departure_time = kwargs.get('departure_time')
        self.arrival_time = kwargs.get('arrival_time')
        self.business_price = kwargs.get('business_price')
        self.economy_price = kwargs.get('economy_price')
        self.first_class_price = kwargs.get('first_class_price')
        self.business_seats_available = kwargs.get('business_seats_available', 0)
        self.economy_seats_available = kwargs.get('economy_seats_available', 0)
        self.first_class_seats_available = kwargs.get('first_class_seats_available', 0)
        self.status = kwargs.get('status', '计划中')
    
    @classmethod
    def get_by_id(cls, flight_id: int) -> Optional['Flight']:
        """根据ID获取航班"""
        data = db.get_by_id('flights', flight_id, 'flight_id')
        return cls(**data) if data else None
    
    @classmethod
    def get_by_number(cls, flight_number: str) -> Optional['Flight']:
        """根据航班号获取航班"""
        data = db.execute_one("SELECT * FROM flights WHERE flight_number = %s", (flight_number,))
        return cls(**data) if data else None
    
    @classmethod
    def search_flights(cls, departure_city: str, arrival_city: str, departure_date: str) -> List['Flight']:
        """搜索航班"""
        query = """
            SELECT f.* FROM flights f
            JOIN routes r ON f.route_id = r.route_id
            WHERE r.departure_city = %s 
            AND r.arrival_city = %s
            AND DATE(f.departure_time) = %s
            AND f.status = '计划中'
            ORDER BY f.departure_time
        """
        data_list = db.execute_query(query, (departure_city, arrival_city, departure_date))
        return [cls(**data) for data in data_list]
    
    def get_route(self) -> Optional[Route]:
        """获取航线信息"""
        return Route.get_by_id(self.route_id)
    
    def get_aircraft(self) -> Optional[Aircraft]:
        """获取飞机型号信息"""
        return Aircraft.get_by_id(self.aircraft_id)
    
    def update_seats(self, seat_class: str, count: int = 1) -> bool:
        """更新座位数量"""
        if seat_class == "经济舱":
            field = "economy_seats_available"
        elif seat_class == "商务舱":
            field = "business_seats_available"
        elif seat_class == "头等舱":
            field = "first_class_seats_available"
        else:
            return False
        
        query = f"UPDATE flights SET {field} = {field} - %s WHERE flight_id = %s"
        result = db.execute_update(query, (count, self.flight_id))
        return result > 0


class Order(BaseModel):
    """订单模型"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order_id = kwargs.get('order_id')
        self.user_id = kwargs.get('user_id')
        self.flight_id = kwargs.get('flight_id')
        self.total_price = kwargs.get('total_price')
        self.payment_status = kwargs.get('payment_status', '待支付')
        self.trip_status = kwargs.get('trip_status', '待值机')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
        self.payment_method = kwargs.get('payment_method')
        self.order_number = kwargs.get('order_number')
    
    @classmethod
    def get_by_id(cls, order_id: int) -> Optional['Order']:
        """根据ID获取订单"""
        data = db.get_by_id('orders', order_id, 'order_id')
        return cls(**data) if data else None
    
    @classmethod
    def get_by_user(cls, user_id: int, status: Optional[str] = None) -> List['Order']:
        """获取用户的订单列表"""
        query = "SELECT * FROM orders WHERE user_id = %s"
        params = [user_id]
        
        if status and status != "all":
            query += " AND trip_status = %s"
            params.append(status)
        
        query += " ORDER BY created_at DESC"
        data_list = db.execute_query(query, tuple(params))
        return [cls(**data) for data in data_list]
    
    def get_user(self) -> Optional[User]:
        """获取用户信息"""
        return User.get_by_id(self.user_id)
    
    def get_flight(self) -> Optional[Flight]:
        """获取航班信息"""
        return Flight.get_by_id(self.flight_id)
    
    def get_passengers(self) -> List['OrderPassenger']:
        """获取订单乘客信息"""
        data_list = db.execute_query(
            "SELECT * FROM order_passengers WHERE order_id = %s",
            (self.order_id,)
        )
        return [OrderPassenger(**data) for data in data_list]


class OrderPassenger(BaseModel):
    """订单乘客模型"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.passenger_id = kwargs.get('passenger_id')
        self.order_id = kwargs.get('order_id')
        self.real_name = kwargs.get('real_name')
        self.id_card = kwargs.get('id_card')
        self.phone = kwargs.get('phone')
        self.seat_class = kwargs.get('seat_class')
    
    @classmethod
    def get_by_order(cls, order_id: int) -> List['OrderPassenger']:
        """获取订单的所有乘客"""
        data_list = db.execute_query(
            "SELECT * FROM order_passengers WHERE order_id = %s",
            (order_id,)
        )
        return [cls(**data) for data in data_list]
    
    def save(self) -> int:
        """保存乘客信息"""
        if self.passenger_id:
            # 更新
            data = self.to_dict()
            data.pop('passenger_id', None)  # 移除id字段
            return db.update('order_passengers', data, 'passenger_id = %s', (self.passenger_id,))
        else:
            # 插入
            data = self.to_dict()
            data.pop('passenger_id', None)  # 移除id字段
            self.passenger_id = db.insert('order_passengers', data)
            return self.passenger_id


class Notice(BaseModel):
    """通知模型"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notice_id = kwargs.get('notice_id')
        self.title = kwargs.get('title')
        self.content = kwargs.get('content')
        self.type = kwargs.get('type', 'info')
        self.is_active = kwargs.get('is_active', True)
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
    
    @classmethod
    def get_by_id(cls, notice_id: int) -> Optional['Notice']:
        """根据ID获取通知"""
        data = db.get_by_id('notices', notice_id, 'notice_id')
        return cls(**data) if data else None
    
    @classmethod
    def get_active_notices(cls) -> List['Notice']:
        """获取所有活跃的通知"""
        data_list = db.execute_query(
            "SELECT * FROM notices WHERE is_active = 1 ORDER BY created_at DESC"
        )
        return [cls(**data) for data in data_list] 