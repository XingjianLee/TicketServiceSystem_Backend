from fastapi import APIRouter, HTTPException, Depends
from app.core.database import db
from app.models.schemas import UserResponse, UserUpdate, UserStats
from app.routers.auth import get_current_user
from typing import List

router = APIRouter()

@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    current_user: dict = Depends(get_current_user)
):
    """获取用户统计信息"""
    # 获取用户订单统计
    order_stats = db.execute_one(
        """SELECT 
               COUNT(*) as total_orders,
               COUNT(CASE WHEN trip_status = '已完成' THEN 1 END) as completed_orders,
               COUNT(CASE WHEN trip_status = '已确认' THEN 1 END) as confirmed_orders,
               COUNT(CASE WHEN trip_status = '待处理' THEN 1 END) as pending_orders
           FROM orders 
           WHERE user_id = %s""",
        (current_user["id"],)
    )
    
    # 获取访问城市统计
    visited_cities = db.execute_query(
        """SELECT DISTINCT r.departure_city, r.arrival_city
           FROM orders o
           JOIN flights f ON o.flight_id = f.flight_id
           JOIN routes r ON f.route_id = r.route_id
           WHERE o.user_id = %s AND o.trip_status = '已完成'""",
        (current_user["id"],)
    )
    
    # 计算总飞行里程（简化计算）
    total_miles = len(visited_cities) * 800  # 假设平均每次飞行800公里
    
    # 计算积分（基于飞行次数）
    points = order_stats["total_orders"] * 500
    
    return UserStats(
        total_flights=order_stats["total_orders"],
        visited_cities=len(set([city for row in visited_cities for city in [row["departure_city"], row["arrival_city"]]])),
        total_miles=total_miles,
        vip_level=current_user.get("vip_level", 0),
        points=points
    )

@router.get("/recent-flights")
async def get_recent_flights(
    current_user: dict = Depends(get_current_user),
    limit: int = 5
):
    """获取最近航班"""
    recent_flights = db.execute_query(
        """SELECT o.order_id, f.flight_number, r.departure_city, r.arrival_city,
                  f.departure_time, o.trip_status
           FROM orders o
           JOIN flights f ON o.flight_id = f.flight_id
           JOIN routes r ON f.route_id = r.route_id
           WHERE o.user_id = %s
           ORDER BY f.departure_time DESC
           LIMIT %s""",
        (current_user["id"], limit)
    )
    
    return [
        {
            "id": flight["order_id"],
            "route": f"{flight['departure_city']} → {flight['arrival_city']}",
            "date": flight["departure_time"].strftime("%Y-%m-%d"),
            "flight_number": flight["flight_number"],
            "status": flight["trip_status"]
        }
        for flight in recent_flights
    ]

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: dict = Depends(get_current_user)
):
    """获取用户资料"""
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        nickname=current_user["nickname"],
        email=current_user["email"],
        phone=current_user["phone"],
        real_name=current_user["real_name"],
        gender=current_user["gender"],
        age=current_user["age"],
        avatar=current_user.get("avatar"),
        signature=current_user.get("signature"),
        vip_level=current_user.get("vip_level", 0),
        company=current_user.get("company"),
        user_type=current_user.get("user_type", "passenger"),
        created_at=current_user["created_at"]
    )

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """更新用户资料"""
    update_fields = []
    update_values = []
    
    for field, value in user_update.dict(exclude_unset=True).items():
        if value is not None:
            update_fields.append(f"{field} = %s")
            update_values.append(value)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="没有提供要更新的字段")
    
    update_values.append(current_user["id"])
    query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
    db.execute_update(query, tuple(update_values))
    
    # 返回更新后的用户信息
    updated_user = db.execute_one("SELECT * FROM users WHERE id = %s", (current_user["id"],))
    return UserResponse(
        id=updated_user["id"],
        username=updated_user["username"],
        nickname=updated_user["nickname"],
        email=updated_user["email"],
        phone=updated_user["phone"],
        real_name=updated_user["real_name"],
        gender=updated_user["gender"],
        age=updated_user["age"],
        avatar=updated_user.get("avatar"),
        signature=updated_user.get("signature"),
        vip_level=updated_user.get("vip_level", 0),
        company=updated_user.get("company"),
        user_type=updated_user.get("user_type", "passenger"),
        created_at=updated_user["created_at"]
    )

@router.get("/orders/summary")
async def get_orders_summary(
    current_user: dict = Depends(get_current_user)
):
    """获取订单统计摘要"""
    # 获取各状态订单数量
    status_counts = db.execute_query(
        """SELECT trip_status, COUNT(*) as count
           FROM orders
           WHERE user_id = %s
           GROUP BY trip_status""",
        (current_user["id"],)
    )
    
    # 转换为字典格式
    summary = {
        "total": 0,
        "completed": 0,
        "confirmed": 0,
        "pending": 0,
        "cancelled": 0
    }
    
    for status_count in status_counts:
        status = status_count["trip_status"]
        count = status_count["count"]
        summary["total"] += count
        
        if status == "已完成":
            summary["completed"] = count
        elif status == "已确认":
            summary["confirmed"] = count
        elif status == "待处理":
            summary["pending"] = count
        elif status == "已取消":
            summary["cancelled"] = count
    
    return summary 