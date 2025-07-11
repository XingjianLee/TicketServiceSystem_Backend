from fastapi import APIRouter, HTTPException, status, Depends
from app.database.models import Order, OrderPassenger, User, Flight
from app.core.security import get_current_user
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter()


class PassengerInfo(BaseModel):
    """乘客信息"""
    real_name: str
    id_card: str
    phone: str
    seat_class: str  # 经济舱、商务舱、头等舱


class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    flight_id: int
    passengers: List[PassengerInfo]
    payment_method: str = "在线支付"


class OrderResponse(BaseModel):
    """订单响应"""
    order_id: int
    order_number: str
    user_id: int
    flight_id: int
    total_price: float
    payment_status: str
    trip_status: str
    created_at: datetime
    payment_method: str
    passengers: List[dict]
    flight_info: dict


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: CreateOrderRequest,
    current_user: User = Depends(get_current_user)
):
    """创建订单"""
    try:
        # 获取航班信息
        flight = Flight.get_by_id(order_data.flight_id)
        if not flight:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="航班不存在"
            )
        
        # 检查座位可用性
        seat_prices = {
            "经济舱": flight.economy_price,
            "商务舱": flight.business_price,
            "头等舱": flight.first_class_price
        }
        
        seat_availability = {
            "经济舱": flight.economy_seats_available,
            "商务舱": flight.business_seats_available,
            "头等舱": flight.first_class_seats_available
        }
        
        # 计算总价并检查座位
        total_price = 0
        for passenger in order_data.passengers:
            seat_class = passenger.seat_class
            if seat_class not in seat_prices:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无效的座位类型: {seat_class}"
                )
            
            if seat_availability[seat_class] <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{seat_class}座位不足"
                )
            
            total_price += seat_prices[seat_class]
        
        # 生成订单号
        order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
        
        # 创建订单
        new_order = Order(
            user_id=current_user.id,
            flight_id=order_data.flight_id,
            total_price=total_price,
            payment_status="待支付",
            trip_status="待值机",
            payment_method=order_data.payment_method,
            order_number=order_number
        )
        
        order_id = new_order.save()
        
        # 创建乘客信息
        passengers_data = []
        for passenger in order_data.passengers:
            passenger_record = OrderPassenger(
                order_id=order_id,
                real_name=passenger.real_name,
                id_card=passenger.id_card,
                phone=passenger.phone,
                seat_class=passenger.seat_class
            )
            passenger_record.save()
            passengers_data.append({
                "real_name": passenger.real_name,
                "id_card": passenger.id_card,
                "phone": passenger.phone,
                "seat_class": passenger.seat_class
            })
        
        # 更新航班座位数量
        for passenger in order_data.passengers:
            flight.update_seats(passenger.seat_class, 1)
        
        # 构建响应数据
        flight_info = {
            "flight_id": flight.flight_id,
            "flight_number": flight.flight_number,
            "airline": flight.airline,
            "departure_time": flight.departure_time,
            "arrival_time": flight.arrival_time
        }
        
        return OrderResponse(
            order_id=order_id,
            order_number=order_number,
            user_id=current_user.id,
            flight_id=order_data.flight_id,
            total_price=total_price,
            payment_status="待支付",
            trip_status="待值机",
            created_at=new_order.created_at,
            payment_method=order_data.payment_method,
            passengers=passengers_data,
            flight_info=flight_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建订单失败: {str(e)}"
        )


@router.get("/", response_model=List[OrderResponse])
async def get_user_orders(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """获取用户订单列表"""
    try:
        orders = Order.get_by_user(current_user.id, status)
        
        order_list = []
        for order in orders:
            flight = order.get_flight()
            passengers = order.get_passengers()
            
            passengers_data = [
                {
                    "real_name": p.real_name,
                    "id_card": p.id_card,
                    "phone": p.phone,
                    "seat_class": p.seat_class
                }
                for p in passengers
            ]
            
            flight_info = {
                "flight_id": flight.flight_id,
                "flight_number": flight.flight_number,
                "airline": flight.airline,
                "departure_time": flight.departure_time,
                "arrival_time": flight.arrival_time
            } if flight else {}
            
            order_response = OrderResponse(
                order_id=order.order_id,
                order_number=order.order_number,
                user_id=order.user_id,
                flight_id=order.flight_id,
                total_price=order.total_price,
                payment_status=order.payment_status,
                trip_status=order.trip_status,
                created_at=order.created_at,
                payment_method=order.payment_method,
                passengers=passengers_data,
                flight_info=flight_info
            )
            order_list.append(order_response)
        
        return order_list
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取订单列表失败: {str(e)}"
        )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user)
):
    """获取订单详情"""
    try:
        order = Order.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        # 检查权限
        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此订单"
            )
        
        flight = order.get_flight()
        passengers = order.get_passengers()
        
        passengers_data = [
            {
                "real_name": p.real_name,
                "id_card": p.id_card,
                "phone": p.phone,
                "seat_class": p.seat_class
            }
            for p in passengers
        ]
        
        flight_info = {
            "flight_id": flight.flight_id,
            "flight_number": flight.flight_number,
            "airline": flight.airline,
            "departure_time": flight.departure_time,
            "arrival_time": flight.arrival_time
        } if flight else {}
        
        return OrderResponse(
            order_id=order.order_id,
            order_number=order.order_number,
            user_id=order.user_id,
            flight_id=order.flight_id,
            total_price=order.total_price,
            payment_status=order.payment_status,
            trip_status=order.trip_status,
            created_at=order.created_at,
            payment_method=order.payment_method,
            passengers=passengers_data,
            flight_info=flight_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取订单详情失败: {str(e)}"
        )


@router.post("/{order_id}/pay")
async def pay_order(
    order_id: int,
    current_user: User = Depends(get_current_user)
):
    """支付订单"""
    try:
        order = Order.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权操作此订单"
            )
        
        if order.payment_status == "已支付":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单已支付"
            )
        
        # 更新支付状态
        order.payment_status = "已支付"
        order.save()
        
        return {"message": "支付成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"支付失败: {str(e)}"
        )


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user)
):
    """取消订单"""
    try:
        order = Order.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权操作此订单"
            )
        
        if order.trip_status in ["已完成", "已取消"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单状态不允许取消"
            )
        
        # 更新订单状态
        order.trip_status = "已取消"
        order.save()
        
        # 退还座位
        passengers = order.get_passengers()
        flight = order.get_flight()
        if flight:
            for passenger in passengers:
                # 这里需要实现退还座位的逻辑
                pass
        
        return {"message": "订单取消成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消订单失败: {str(e)}"
        ) 