from fastapi import APIRouter, HTTPException
from app.core.database import db
from app.models.schemas import FlightSearch, FlightResponse
from typing import List
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/search", response_model=List[FlightResponse])
async def search_flights(
    from_city: str,
    to_city: str,
    departure_date: str,
    passengers: int = 1,
    seat_class: str = None,
    trip_type: str = "oneWay"
):
    """搜索航班"""
    try:
        # 解析日期
        search_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD 格式")
    
    # 构建查询条件
    query = """
        SELECT f.*, r.departure_city, r.arrival_city, a.airline_name
        FROM flights f
        JOIN routes r ON f.route_id = r.route_id
        JOIN airlines a ON f.airline_id = a.airline_id
        WHERE r.departure_city = %s 
        AND r.arrival_city = %s
        AND DATE(f.departure_time) = %s
        AND f.status = '计划中'
    """
    params = [from_city, to_city, search_date]
    
    # 如果指定了舱位类型，添加舱位可用性检查
    if seat_class:
        if seat_class == "经济舱":
            query += " AND f.economy_seats_available >= %s"
            params.append(passengers)
        elif seat_class == "商务舱":
            query += " AND f.business_seats_available >= %s"
            params.append(passengers)
        elif seat_class == "头等舱":
            query += " AND f.first_class_seats_available >= %s"
            params.append(passengers)
    
    query += " ORDER BY f.departure_time"
    
    flights = db.execute_query(query, tuple(params))
    
    # 转换为前端期望的格式
    formatted_flights = []
    for flight in flights:
        # 计算飞行时长
        departure_time = flight["departure_time"]
        arrival_time = flight["arrival_time"]
        duration = arrival_time - departure_time
        duration_str = f"{duration.seconds // 3600}h {(duration.seconds % 3600) // 60}m"
        
        # 确定价格和可用座位数
        if seat_class == "经济舱" or not seat_class:
            price = flight["economy_price"]
            seats_available = flight["economy_seats_available"]
            class_type = "Economy"
        elif seat_class == "商务舱":
            price = flight["business_price"]
            seats_available = flight["business_seats_available"]
            class_type = "Business"
        elif seat_class == "头等舱":
            price = flight["first_class_price"]
            seats_available = flight["first_class_seats_available"]
            class_type = "First"
        
        formatted_flight = {
            "id": flight["flight_id"],
            "airline": flight["airline_name"],
            "flight_number": flight["flight_number"],
            "departure": {
                "city": flight["departure_city"],
                "time": departure_time.strftime("%H:%M"),
                "airport": f"{flight['departure_city']}机场"
            },
            "arrival": {
                "city": flight["arrival_city"],
                "time": arrival_time.strftime("%H:%M"),
                "airport": f"{flight['arrival_city']}机场"
            },
            "duration": duration_str,
            "price": price,
            "class_type": class_type,
            "seats_available": seats_available,
            "status": flight["status"]
        }
        formatted_flights.append(formatted_flight)
    
    return formatted_flights

@router.get("/{flight_id}", response_model=FlightResponse)
async def get_flight_detail(flight_id: int):
    """获取航班详情"""
    flight = db.execute_one(
        """SELECT f.*, r.departure_city, r.arrival_city, a.airline_name
           FROM flights f
           JOIN routes r ON f.route_id = r.route_id
           JOIN airlines a ON f.airline_id = a.airline_id
           WHERE f.flight_id = %s""",
        (flight_id,)
    )
    
    if not flight:
        raise HTTPException(status_code=404, detail="航班不存在")
    
    # 计算飞行时长
    departure_time = flight["departure_time"]
    arrival_time = flight["arrival_time"]
    duration = arrival_time - departure_time
    duration_str = f"{duration.seconds // 3600}h {(duration.seconds % 3600) // 60}m"
    
    return {
        "id": flight["flight_id"],
        "airline": flight["airline_name"],
        "flight_number": flight["flight_number"],
        "departure": {
            "city": flight["departure_city"],
            "time": departure_time.strftime("%H:%M"),
            "airport": f"{flight['departure_city']}机场"
        },
        "arrival": {
            "city": flight["arrival_city"],
            "time": arrival_time.strftime("%H:%M"),
            "airport": f"{flight['arrival_city']}机场"
        },
        "duration": duration_str,
        "price": flight["economy_price"],
        "class_type": "Economy",
        "seats_available": flight["economy_seats_available"],
        "status": flight["status"]
    }

@router.get("/")
async def get_all_flights():
    """获取所有航班（用于管理）"""
    flights = db.execute_query(
        """SELECT f.*, r.departure_city, r.arrival_city, a.airline_name
           FROM flights f
           JOIN routes r ON f.route_id = r.route_id
           JOIN airlines a ON f.airline_id = a.airline_id
           ORDER BY f.departure_time DESC
           LIMIT 50"""
    )
    return flights 