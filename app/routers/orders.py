from fastapi import APIRouter, HTTPException, Depends
from app.core.database import db
from app.models.schemas import OrderCreate, OrderResponse, MessageResponse, SeatSelect
from app.routers.auth import get_current_user
from datetime import datetime
import uuid
from typing import List

router = APIRouter()

@router.get("/", response_model=List[OrderResponse])
async def get_user_orders(
    current_user: dict = Depends(get_current_user),
    status: str = None
):
    """获取用户订单列表"""
    query = """
        SELECT o.*, f.flight_number, r.departure_city, r.arrival_city, 
               f.departure_time, f.arrival_time, op.seat_number, op.seat_class, op.price
        FROM orders o
        JOIN flights f ON o.flight_id = f.flight_id
        JOIN routes r ON f.route_id = r.route_id
        LEFT JOIN order_passengers op ON o.order_id = op.order_id
        WHERE o.user_id = %s
    """
    params = [current_user["id"]]
    
    if status and status != "all":
        query += " AND o.trip_status = %s"
        params.append(status)
    
    query += " ORDER BY o.created_at DESC"
    
    orders_data = db.execute_query(query, tuple(params))
    
    # 按订单分组
    orders_dict = {}
    for row in orders_data:
        order_id = row["order_id"]
        if order_id not in orders_dict:
            orders_dict[order_id] = {
                "id": str(order_id),
                "order_id": order_id,
                "order_number": row["order_number"],
                "flight_number": row["flight_number"],
                "route": f"{row['departure_city']} → {row['arrival_city']}",
                "date": row["departure_time"].strftime("%Y-%m-%d"),
                "time": f"{row['departure_time'].strftime('%H:%M')} - {row['arrival_time'].strftime('%H:%M')}",
                "passengers": 1,  # 简化处理
                "class_type": row["seat_class"],
                "price": row["price"],
                "status": row["trip_status"],
                "booking_date": row["created_at"].strftime("%Y-%m-%d"),
                "seat_number": row["seat_number"],
                "total_price": row["total_price"],
                "payment_status": row["payment_status"],
                "trip_status": row["trip_status"],
                "created_at": row["created_at"]
            }
    
    return list(orders_dict.values())

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    """创建订单"""
    # 检查航班是否存在
    flight = db.execute_one("SELECT * FROM flights WHERE flight_id = %s", (order_data.flight_id,))
    if not flight:
        raise HTTPException(status_code=404, detail="航班不存在")
    
    # 计算总价
    total_price = 0
    for passenger in order_data.passengers:
        if passenger.seat_class == "经济舱":
            price = flight["economy_price"]
        elif passenger.seat_class == "商务舱":
            price = flight["business_price"]
        elif passenger.seat_class == "头等舱":
            price = flight["first_class_price"]
        else:
            raise HTTPException(status_code=400, detail=f"不支持的舱位类型: {passenger.seat_class}")
        
        total_price += price
    
    # 生成订单号
    order_number = f"BT{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8].upper()}"
    
    # 创建订单
    order_id = db.execute_insert(
        """INSERT INTO orders (user_id, flight_id, total_price, order_number) 
           VALUES (%s, %s, %s, %s)""",
        (current_user["id"], order_data.flight_id, total_price, order_number)
    )
    
    # 创建乘机人信息
    for passenger in order_data.passengers:
        if passenger.seat_class == "经济舱":
            price = flight["economy_price"]
        elif passenger.seat_class == "商务舱":
            price = flight["business_price"]
        elif passenger.seat_class == "头等舱":
            price = flight["first_class_price"]
        
        db.execute_insert(
            """INSERT INTO order_passengers 
               (order_id, passenger_name, id_card, phone, seat_class, price) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (order_id, passenger.passenger_name, passenger.id_card, 
             passenger.phone, passenger.seat_class, price)
        )
    
    # 更新航班座位数
    for passenger in order_data.passengers:
        if passenger.seat_class == "经济舱":
            db.execute_update(
                "UPDATE flights SET economy_seats_available = economy_seats_available - 1 WHERE flight_id = %s",
                (order_data.flight_id,)
            )
        elif passenger.seat_class == "商务舱":
            db.execute_update(
                "UPDATE flights SET business_seats_available = business_seats_available - 1 WHERE flight_id = %s",
                (order_data.flight_id,)
            )
        elif passenger.seat_class == "头等舱":
            db.execute_update(
                "UPDATE flights SET first_class_seats_available = first_class_seats_available - 1 WHERE flight_id = %s",
                (order_data.flight_id,)
            )
    
    # 返回创建的订单
    return await get_order_detail(order_id, current_user)

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_detail(
    order_id: int,
    current_user: dict = Depends(get_current_user)
):
    """获取订单详情"""
    order = db.execute_one(
        """SELECT o.*, f.flight_number, r.departure_city, r.arrival_city, 
                  f.departure_time, f.arrival_time, op.seat_number, op.seat_class, op.price
           FROM orders o
           JOIN flights f ON o.flight_id = f.flight_id
           JOIN routes r ON f.route_id = r.route_id
           LEFT JOIN order_passengers op ON o.order_id = op.order_id
           WHERE o.order_id = %s AND o.user_id = %s""",
        (order_id, current_user["id"])
    )
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    return {
        "id": str(order["order_id"]),
        "order_id": order["order_id"],
        "order_number": order["order_number"],
        "flight_number": order["flight_number"],
        "route": f"{order['departure_city']} → {order['arrival_city']}",
        "date": order["departure_time"].strftime("%Y-%m-%d"),
        "time": f"{order['departure_time'].strftime('%H:%M')} - {order['arrival_time'].strftime('%H:%M')}",
        "passengers": 1,
        "class_type": order["seat_class"],
        "price": order["price"],
        "status": order["trip_status"],
        "booking_date": order["created_at"].strftime("%Y-%m-%d"),
        "seat_number": order["seat_number"],
        "total_price": order["total_price"],
        "payment_status": order["payment_status"],
        "trip_status": order["trip_status"],
        "created_at": order["created_at"]
    }

@router.post("/{order_id}/seat", response_model=MessageResponse)
async def select_seat(
    order_id: int,
    seat_data: SeatSelect,
    current_user: dict = Depends(get_current_user)
):
    """为订单选择座位"""
    # 检查订单是否存在且属于当前用户
    order = db.execute_one(
        "SELECT * FROM orders WHERE order_id = %s AND user_id = %s",
        (order_id, current_user["id"])
    )
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 检查订单状态
    if order["trip_status"] != "已确认":
        raise HTTPException(status_code=400, detail="只有已确认的订单才能选座")
    
    # 检查座位是否已被占用
    existing_seat = db.execute_one(
        "SELECT * FROM order_passengers WHERE order_id = %s AND seat_number = %s",
        (order_id, seat_data.seat_number)
    )
    
    if existing_seat:
        raise HTTPException(status_code=400, detail="该座位已被占用")
    
    # 更新座位号
    db.execute_update(
        "UPDATE order_passengers SET seat_number = %s WHERE order_id = %s",
        (seat_data.seat_number, order_id)
    )
    
    return MessageResponse(message="选座成功")

@router.put("/{order_id}/pay", response_model=MessageResponse)
async def pay_order(
    order_id: int,
    payment_method: str,
    current_user: dict = Depends(get_current_user)
):
    """支付订单"""
    order = db.execute_one(
        "SELECT * FROM orders WHERE order_id = %s AND user_id = %s",
        (order_id, current_user["id"])
    )
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if order["payment_status"] == "已支付":
        raise HTTPException(status_code=400, detail="订单已支付")
    
    if order["payment_status"] == "已取消":
        raise HTTPException(status_code=400, detail="订单已取消，无法支付")
    
    # 更新订单状态
    db.execute_update(
        "UPDATE orders SET payment_status = '已支付', payment_method = %s, updated_at = NOW() WHERE order_id = %s",
        (payment_method, order_id)
    )
    
    return MessageResponse(message="支付成功")

@router.delete("/{order_id}", response_model=MessageResponse)
async def cancel_order(
    order_id: int,
    current_user: dict = Depends(get_current_user)
):
    """取消订单"""
    order = db.execute_one(
        "SELECT * FROM orders WHERE order_id = %s AND user_id = %s",
        (order_id, current_user["id"])
    )
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if order["trip_status"] == "已完成":
        raise HTTPException(status_code=400, detail="已完成的订单无法取消")
    
    if order["trip_status"] == "已取消":
        raise HTTPException(status_code=400, detail="订单已取消")
    
    # 更新订单状态
    db.execute_update(
        "UPDATE orders SET trip_status = '已取消', updated_at = NOW() WHERE order_id = %s",
        (order_id,)
    )
    
    return MessageResponse(message="订单已取消") 