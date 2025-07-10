from fastapi import APIRouter, HTTPException, Depends
from app.core.database import db
from app.models.schemas import Notice, NoticeCreate, MessageResponse
from app.routers.auth import get_current_user
from typing import List
from datetime import datetime, timedelta

router = APIRouter()

# 通知记录
MOCK_NOTICES = [
    {
        "id": 1,
        "title": "欢迎使用蓝天航空票务系统",
        "content": "感谢您选择蓝天航空！我们致力于为您提供最优质的航空服务体验。如有任何问题，请随时联系我们的客服团队。",
        "type": "info",
        "created_at": datetime.now() - timedelta(days=5),
        "is_read": False
    },
    {
        "id": 2,
        "title": "系统维护通知",
        "content": "为了提供更好的服务，我们将在2024年1月20日凌晨2:00-4:00进行系统维护。期间可能影响在线订票功能，请您提前安排行程。",
        "type": "warning",
        "created_at": datetime.now() - timedelta(days=3),
        "is_read": False
    },
    {
        "id": 3,
        "title": "春节特惠活动",
        "content": "春节将至，蓝天航空推出特惠活动！1月15日-2月15日期间，所有国内航线享受8折优惠，商务舱更有额外折扣。详情请查看活动页面。",
        "type": "success",
        "created_at": datetime.now() - timedelta(days=2),
        "is_read": True
    },
    {
        "id": 4,
        "title": "航班延误提醒",
        "content": "您预订的CA1234航班（北京-上海）因天气原因延误2小时，新的起飞时间为10:30。我们深表歉意，并将为您提供相应的补偿。",
        "type": "error",
        "created_at": datetime.now() - timedelta(hours=6),
        "is_read": False
    },
    {
        "id": 5,
        "title": "会员积分到账",
        "content": "恭喜您！您的最近一次飞行已获得500积分，当前总积分为2,350分。积分可用于兑换免费机票或升级服务。",
        "type": "success",
        "created_at": datetime.now() - timedelta(hours=2),
        "is_read": False
    },
    {
        "id": 6,
        "title": "在线选座功能上线",
        "content": "好消息！蓝天航空在线选座功能现已正式上线。您可以在航班起飞前24小时为已确认的订单选择座位，让您的旅程更加舒适。",
        "type": "info",
        "created_at": datetime.now() - timedelta(hours=1),
        "is_read": False
    }
]


@router.get("/", response_model=List[Notice])
async def get_notices(
        current_user: dict = Depends(get_current_user),
        unread_only: bool = False
):
    """获取通知列表"""
    notices = MOCK_NOTICES.copy()

    if unread_only:
        notices = [notice for notice in notices if not notice["is_read"]]

    return notices


@router.get("/{notice_id}", response_model=Notice)
async def get_notice_detail(
        notice_id: int,
        current_user: dict = Depends(get_current_user)
):
    """获取通知详情"""
    notice = next((notice for notice in MOCK_NOTICES if notice["id"] == notice_id), None)

    if not notice:
        raise HTTPException(status_code=404, detail="通知不存在")

    return notice


@router.post("/{notice_id}/read", response_model=MessageResponse)
async def mark_notice_read(
        notice_id: int,
        current_user: dict = Depends(get_current_user)
):
    """标记通知为已读"""
    notice = next((notice for notice in MOCK_NOTICES if notice["id"] == notice_id), None)

    if not notice:
        raise HTTPException(status_code=404, detail="通知不存在")

    # 在实际应用中，这里会更新数据库
    # 现在只是返回成功消息
    return MessageResponse(message="已标记为已读")


@router.post("/read-all", response_model=MessageResponse)
async def mark_all_notices_read(
        current_user: dict = Depends(get_current_user)
):
    """标记所有通知为已读"""
    unread_count = len([notice for notice in MOCK_NOTICES if not notice["is_read"]])

    # 在实际应用中，这里会批量更新数据库
    # 现在只是返回成功消息
    return MessageResponse(message=f"已标记 {unread_count} 条通知为已读")


@router.get("/unread/count")
async def get_unread_count(
        current_user: dict = Depends(get_current_user)
):
    """获取未读通知数量"""
    unread_count = len([notice for notice in MOCK_NOTICES if not notice["is_read"]])
    return {"unread_count": unread_count}
