# -*- coding: utf-8 -*-
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
import re


class UserRegisterRequest(BaseModel):
    """用户注册请求模型"""
    username: str
    email: EmailStr
    password: str
    confirm_password: str
    phone: str
    id_card: str
    real_name: str
    gender: Optional[str] = "未知"
    age: Optional[int] = None
    user_type: str = "passenger"
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('用户名长度必须在3-50个字符之间')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度至少6位')
        return v
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('两次输入的密码不一致')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('请输入有效的手机号码')
        return v
    
    @validator('id_card')
    def validate_id_card(cls, v):
        if not re.match(r'^\d{17}[\dXx]$', v):
            raise ValueError('请输入有效的身份证号码')
        return v
    
    @validator('gender')
    def validate_gender(cls, v):
        if v not in ['男', '女', '未知']:
            raise ValueError('性别只能是：男、女、未知')
        return v
    
    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 0 or v > 120):
            raise ValueError('年龄必须在0-120之间')
        return v


class UserLoginRequest(BaseModel):
    """用户登录请求模型"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户信息响应模型"""
    id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    signature: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    real_name: Optional[str] = None
    gender: str = "未知"
    age: Optional[int] = None
    vip_level: int = 0
    user_type: str = "passenger"
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    """用户信息更新请求模型"""
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    signature: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    real_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('请输入有效的手机号码')
        return v
    
    @validator('gender')
    def validate_gender(cls, v):
        if v and v not in ['男', '女', '未知']:
            raise ValueError('性别只能是：男、女、未知')
        return v
    
    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 0 or v > 120):
            raise ValueError('年龄必须在0-120之间')
        return v


class LoginResponse(BaseModel):
    """登录响应模型"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token数据模型"""
    username: Optional[str] = None
    user_id: Optional[int] = None 