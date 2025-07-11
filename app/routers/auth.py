# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials
from app.schemas.user import UserRegisterRequest, UserLoginRequest, LoginResponse, UserResponse
from app.database.models import User
from app.core.security import get_password_hash, verify_password, create_user_token, get_current_user, security
from typing import Optional
from datetime import datetime

router = APIRouter()

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegisterRequest):
    """用户注册（明文密码存储）"""
    try:
        # 检查用户名是否已存在
        existing_user = User.get_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        existing_email = User.get_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        
        # 检查身份证号是否已存在
        existing_id_card = User.get_by_id_card(user_data.id_card)
        if existing_id_card:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="身份证号已被注册"
            )
        
        # 明文存储密码
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,  # 明文
            phone=user_data.phone,
            id_card=user_data.id_card,
            real_name=user_data.real_name,
            gender=user_data.gender,
            age=user_data.age,
            user_type=user_data.user_type,
            vip_level=0,
            created_at=datetime.now()
        )
        
        # 保存用户
        user_id = new_user.save()
        
        return {
            "message": "注册成功",
            "user_id": user_id,
            "username": user_data.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )

@router.post("/login", response_model=LoginResponse)
async def login(user_data: UserLoginRequest):
    """用户登录（支持用户名、邮箱、手机号，明文密码比对）"""
    try:
        # 先按用户名查找
        user = User.get_by_username(user_data.username)
        # 如果不是用户名，再按邮箱
        if not user:
            user = User.get_by_email(user_data.username)
        # 如果还不是，再按手机号
        if not user:
            user = User.get_by_phone(user_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名/邮箱/手机号或密码错误"
            )
        # 明文比对密码
        if user_data.password != user.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名/邮箱/手机号或密码错误"
            )
        # 补全 created_at
        created_at = user.created_at or datetime.now()
        user_response = UserResponse(
            id=user.id,
            username=user.username,
            nickname=user.nickname,
            avatar=user.avatar,
            signature=user.signature,
            email=user.email,
            phone=user.phone,
            real_name=user.real_name,
            gender=user.gender,
            age=user.age,
            vip_level=user.vip_level,
            user_type=user.user_type,
            created_at=created_at
        )
        access_token = create_user_token(user.id, user.username)
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """用户登出"""
    # 在实际应用中，可以将token加入黑名单
    return {"message": "登出成功"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        nickname=current_user.nickname,
        avatar=current_user.avatar,
        signature=current_user.signature,
        email=current_user.email,
        phone=current_user.phone,
        real_name=current_user.real_name,
        gender=current_user.gender,
        age=current_user.age,
        vip_level=current_user.vip_level,
        user_type=current_user.user_type,
        created_at=current_user.created_at
    )


@router.post("/refresh")
async def refresh_token(current_user: User = Depends(get_current_user)):
    """刷新访问令牌"""
    access_token = create_user_token(current_user.id, current_user.username)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    } 