# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, status, Query
from app.database.models import Flight, Route, Aircraft
from typing import List, Optional
from datetime import datetime

router = APIRouter()


@router.get("/search")
async def search_flights(
    departure_city: str = Query(..., description="出发城市"),
    arrival_city: str = Query(..., description="到达城市"),
    departure_date: str = Query(..., description="出发日期 (YYYY-MM-DD)")
):
    """搜索航班"""
    try:
        # 验证日期格式
        try:
            datetime.strptime(departure_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="日期格式错误，请使用 YYYY-MM-DD 格式"
            )
        
        flights = Flight.search_flights(departure_city, arrival_city, departure_date)
        
        # 构建响应数据
        flight_list = []
        for flight in flights:
            route = flight.get_route()
            aircraft = flight.get_aircraft()
            
            flight_data = {
                "flight_id": flight.flight_id,
                "flight_number": flight.flight_number,
                "airline": flight.airline,
                "departure_city": route.departure_city if route else None,
                "arrival_city": route.arrival_city if route else None,
                "departure_time": flight.departure_time,
                "arrival_time": flight.arrival_time,
                "business_price": flight.business_price,
                "economy_price": flight.economy_price,
                "first_class_price": flight.first_class_price,
                "business_seats_available": flight.business_seats_available,
                "economy_seats_available": flight.economy_seats_available,
                "first_class_seats_available": flight.first_class_seats_available,
                "status": flight.status,
                "aircraft_model": aircraft.model_name if aircraft else None
            }
            flight_list.append(flight_data)
        
        return {
            "flights": flight_list,
            "total": len(flight_list)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索航班失败: {str(e)}"
        )


@router.get("/{flight_id}")
async def get_flight(flight_id: int):
    """获取航班详情"""
    try:
        flight = Flight.get_by_id(flight_id)
        if not flight:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="航班不存在"
            )
        
        route = flight.get_route()
        aircraft = flight.get_aircraft()
        
        flight_data = {
            "flight_id": flight.flight_id,
            "flight_number": flight.flight_number,
            "airline": flight.airline,
            "departure_city": route.departure_city if route else None,
            "arrival_city": route.arrival_city if route else None,
            "departure_time": flight.departure_time,
            "arrival_time": flight.arrival_time,
            "business_price": flight.business_price,
            "economy_price": flight.economy_price,
            "first_class_price": flight.first_class_price,
            "business_seats_available": flight.business_seats_available,
            "economy_seats_available": flight.economy_seats_available,
            "first_class_seats_available": flight.first_class_seats_available,
            "status": flight.status,
            "aircraft_model": aircraft.model_name if aircraft else None,
            "distance_km": route.distance_km if route else None
        }
        
        return flight_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取航班详情失败: {str(e)}"
        )


@router.get("/")
async def get_all_flights(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数")
):
    """获取所有航班"""
    try:
        # 这里可以添加分页查询逻辑
        query = """
            SELECT f.*, r.departure_city, r.arrival_city, a.model_name as aircraft_model
            FROM flights f
            LEFT JOIN routes r ON f.route_id = r.route_id
            LEFT JOIN aircraft a ON f.aircraft_id = a.aircraft_id
            ORDER BY f.departure_time DESC
            LIMIT %s OFFSET %s
        """
        
        from app.database.database import get_database
        db = get_database()
        data_list = db.execute_query(query, (limit, skip))
        
        return {
            "flights": data_list,
            "total": len(data_list)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取航班列表失败: {str(e)}"
        ) 