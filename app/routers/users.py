from fastapi import APIRouter, HTTPException, Depends
from app.core.database import db
from app.models.schemas import UserUpdate, UserResponse, MessageResponse
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)

@router.put("/profile", response_model=MessageResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    # 构建更新字段
    update_fields = []
    update_values = []
    
    for field, value in user_update.dict(exclude_unset=True).items():
        if value is not None:
            update_fields.append(f"{field} = %s")
            update_values.append(value)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="没有提供要更新的字段")
    
    # 添加用户ID到参数中
    update_values.append(current_user["id"])
    
    # 执行更新
    query = f"UPDATE users SET {', '.join(update_fields)}, updated_at = NOW() WHERE id = %s"
    db.execute_update(query, tuple(update_values))
    
    return MessageResponse(message="用户信息更新成功")

@router.get("/orders")
async def get_user_orders(current_user: dict = Depends(get_current_user)):
    """获取用户的订单列表"""
    orders = db.execute_query(
        """SELECT o.*, f.flight_number, f.airline, r.departure_city, r.arrival_city
           FROM orders o
           JOIN flights f ON o.flight_id = f.flight_id
           JOIN routes r ON f.route_id = r.route_id
           WHERE o.user_id = %s
           ORDER BY o.created_at DESC""",
        (current_user["id"],)
    )
    
    # 获取每个订单的乘机人信息
    for order in orders:
        passengers = db.execute_query(
            "SELECT * FROM order_passengers WHERE order_id = %s",
            (order["order_id"],)
        )
        order["passengers"] = passengers
    
    return orders 