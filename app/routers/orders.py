from fastapi import APIRouter, HTTPException, Depends
from app.core.database import db
from app.models.schemas import OrderCreate, OrderResponse, MessageResponse
from app.routers.auth import get_current_user
from datetime import datetime
import uuid

router = APIRouter()

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
    order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8].upper()}"
    
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
    order = db.execute_one("SELECT * FROM orders WHERE order_id = %s", (order_id,))
    passengers = db.execute_query(
        "SELECT * FROM order_passengers WHERE order_id = %s",
        (order_id,)
    )
    
    return OrderResponse(
        order_id=order["order_id"],
        order_number=order["order_number"],
        total_price=order["total_price"],
        payment_status=order["payment_status"],
        trip_status=order["trip_status"],
        created_at=order["created_at"],
        passengers=passengers
    )

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_detail(
    order_id: int,
    current_user: dict = Depends(get_current_user)
):
    """获取订单详情"""
    order = db.execute_one(
        "SELECT * FROM orders WHERE order_id = %s AND user_id = %s",
        (order_id, current_user["id"])
    )
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    passengers = db.execute_query(
        "SELECT * FROM order_passengers WHERE order_id = %s",
        (order_id,)
    )
    
    return OrderResponse(
        order_id=order["order_id"],
        order_number=order["order_number"],
        total_price=order["total_price"],
        payment_status=order["payment_status"],
        trip_status=order["trip_status"],
        created_at=order["created_at"],
        passengers=passengers
    )

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