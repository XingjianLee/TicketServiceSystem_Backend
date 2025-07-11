from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.user import UserResponse, UserUpdateRequest
from app.database.models import User
from app.core.security import get_current_user, get_password_hash
from typing import List

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """获取用户列表（管理员功能）"""
    # 这里可以添加管理员权限检查
    try:
        users = User.get_all(skip=skip, limit=limit)
        return [
            UserResponse(
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
                created_at=user.created_at
            )
            for user in users
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户列表失败: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """根据ID获取用户信息"""
    try:
        user = User.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return UserResponse(
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
            created_at=user.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """更新当前用户信息"""
    try:
        # 更新用户信息
        update_data = user_data.dict(exclude_unset=True)
        
        # 如果更新邮箱，检查是否已被其他用户使用
        if 'email' in update_data and update_data['email'] != current_user.email:
            existing_user = User.get_by_email(update_data['email'])
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已被其他用户使用"
                )
        
        # 如果更新手机号，检查是否已被其他用户使用
        if 'phone' in update_data and update_data['phone'] != current_user.phone:
            existing_user = User.get_by_phone(update_data['phone'])
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="手机号已被其他用户使用"
                )
        
        # 应用更新
        for field, value in update_data.items():
            setattr(current_user, field, value)
        
        # 保存更新
        current_user.save()
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户信息失败: {str(e)}"
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """更新指定用户信息（管理员功能）"""
    try:
        # 这里可以添加管理员权限检查
        target_user = User.get_by_id(user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 更新用户信息
        update_data = user_data.dict(exclude_unset=True)
        
        # 检查唯一性约束
        if 'email' in update_data and update_data['email'] != target_user.email:
            existing_user = User.get_by_email(update_data['email'])
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已被其他用户使用"
                )
        
        if 'phone' in update_data and update_data['phone'] != target_user.phone:
            existing_user = User.get_by_phone(update_data['phone'])
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="手机号已被其他用户使用"
                )
        
        # 应用更新
        for field, value in update_data.items():
            setattr(target_user, field, value)
        
        # 保存更新
        target_user.save()
        
        return UserResponse(
            id=target_user.id,
            username=target_user.username,
            nickname=target_user.nickname,
            avatar=target_user.avatar,
            signature=target_user.signature,
            email=target_user.email,
            phone=target_user.phone,
            real_name=target_user.real_name,
            gender=target_user.gender,
            age=target_user.age,
            vip_level=target_user.vip_level,
            user_type=target_user.user_type,
            created_at=target_user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户信息失败: {str(e)}"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """删除用户（管理员功能）"""
    try:
        # 这里可以添加管理员权限检查
        target_user = User.get_by_id(user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 删除用户
        User.delete_by_id(user_id)
        
        return {"message": "用户删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除用户失败: {str(e)}"
        ) 