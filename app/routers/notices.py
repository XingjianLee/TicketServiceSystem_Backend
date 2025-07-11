# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, status
from app.database.models import Notice
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class NoticeResponse(BaseModel):
    """通知响应模型"""
    notice_id: int
    title: str
    content: str
    type: str
    priority: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


@router.get("/", response_model=List[NoticeResponse])
async def get_notices():
    """获取所有活跃通知"""
    try:
        notices = Notice.get_active_notices()
        
        notice_list = []
        for notice in notices:
            notice_response = NoticeResponse(
                notice_id=notice.notice_id,
                title=notice.title,
                content=notice.content,
                type=notice.type,
                priority=notice.priority,
                is_active=notice.is_active,
                created_at=notice.created_at,
                updated_at=notice.updated_at
            )
            notice_list.append(notice_response)
        
        return notice_list
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取通知列表失败: {str(e)}"
        )


@router.get("/{notice_id}", response_model=NoticeResponse)
async def get_notice(notice_id: int):
    """获取通知详情"""
    try:
        notice = Notice.get_by_id(notice_id)
        if not notice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="通知不存在"
            )
        
        return NoticeResponse(
            notice_id=notice.notice_id,
            title=notice.title,
            content=notice.content,
            type=notice.type,
            priority=notice.priority,
            is_active=notice.is_active,
            created_at=notice.created_at,
            updated_at=notice.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取通知详情失败: {str(e)}"
        ) 