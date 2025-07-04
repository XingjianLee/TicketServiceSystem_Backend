from fastapi import APIRouter, HTTPException
from app.core.database import db
from app.models.schemas import FlightSearch, FlightResponse
from typing import List
from datetime import datetime

router = APIRouter()

@router.get("/search", response_model=List[FlightResponse])
async def search_flights(
    from_city: str,
    to_city: str,
    departure_date: str,
    seat_class: str = None
):
    """搜索航班"""
    try:
        # 解析日期
        search_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD 格式")
    
    # 构建查询条件
    query = """
        SELECT f.*, r.departure_city, r.arrival_city
        FROM flights f
        JOIN routes r ON f.route_id = r.route_id
        WHERE r.departure_city = %s 
        AND r.arrival_city = %s
        AND DATE(f.departure_time) = %s
        AND f.status = '计划中'
    """
    params = [from_city, to_city, search_date]
    
    # 如果指定了舱位类型，添加舱位可用性检查
    if seat_class:
        if seat_class == "经济舱":
            query += " AND f.economy_seats_available > 0"
        elif seat_class == "商务舱":
            query += " AND f.business_seats_available > 0"
        elif seat_class == "头等舱":
            query += " AND f.first_class_seats_available > 0"
    
    query += " ORDER BY f.departure_time"
    
    flights = db.execute_query(query, tuple(params))
    return flights

@router.get("/{flight_id}", response_model=FlightResponse)
async def get_flight_detail(flight_id: int):
    """获取航班详情"""
    flight = db.execute_one(
        """SELECT f.*, r.departure_city, r.arrival_city
           FROM flights f
           JOIN routes r ON f.route_id = r.route_id
           WHERE f.flight_id = %s""",
        (flight_id,)
    )
    
    if not flight:
        raise HTTPException(status_code=404, detail="航班不存在")
    
    return flight

@router.get("/")
async def get_all_flights():
    """获取所有航班（用于管理）"""
    flights = db.execute_query(
        """SELECT f.*, r.departure_city, r.arrival_city
           FROM flights f
           JOIN routes r ON f.route_id = r.route_id
           ORDER BY f.departure_time DESC
           LIMIT 50"""
    )
    return flights 