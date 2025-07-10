#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建测试账户和基础数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import db
from app.core.config import settings
from passlib.context import CryptContext
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def init_test_user():
    """初始化测试用户"""
    print("正在初始化测试用户...")
    
    # 检查测试用户是否已存在
    existing_user = db.execute_one(
        "SELECT id FROM users WHERE email = %s OR username = %s",
        ('admin@example.com', 'admin')
    )
    
    if existing_user:
        print("测试用户已存在，跳过创建")
        return existing_user['id']
    
    # 创建测试用户
    hashed_password = get_password_hash('123456')
    user_id = db.execute_insert(
        """INSERT INTO users (username, nickname, password, email, phone, id_card, real_name, gender, age, company, user_type, vip_level) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        ('admin', '管理员', hashed_password, 'admin@example.com', '13800138000', 
         '110101199001011234', '管理员', '男', 30, '蓝天航空', 'passenger', 1)
    )
    
    print(f"测试用户创建成功，ID: {user_id}")
    return user_id

def init_notices():
    """初始化通知数据"""
    print("正在初始化通知数据...")
    
    # 检查是否已有通知数据
    existing_notices = db.execute_one("SELECT COUNT(*) as count FROM notices")
    if existing_notices and existing_notices['count'] > 0:
        print("通知数据已存在，跳过创建")
        return
    
    # 创建通知数据
    notices = [
        {
            'title': '欢迎使用蓝天航空票务系统',
            'content': '感谢您选择蓝天航空！我们致力于为您提供最优质的航空服务体验。如有任何问题，请随时联系我们的客服团队。',
            'type': 'info',
            'created_at': datetime.now() - timedelta(days=5)
        },
        {
            'title': '系统维护通知',
            'content': '为了提供更好的服务，我们将在2024年1月20日凌晨2:00-4:00进行系统维护。期间可能影响在线订票功能，请您提前安排行程。',
            'type': 'warning',
            'created_at': datetime.now() - timedelta(days=3)
        },
        {
            'title': '春节特惠活动',
            'content': '春节将至，蓝天航空推出特惠活动！1月15日-2月15日期间，所有国内航线享受8折优惠，商务舱更有额外折扣。详情请查看活动页面。',
            'type': 'success',
            'created_at': datetime.now() - timedelta(days=2)
        },
        {
            'title': '航班延误提醒',
            'content': '您预订的CA1234航班（北京-上海）因天气原因延误2小时，新的起飞时间为10:30。我们深表歉意，并将为您提供相应的补偿。',
            'type': 'error',
            'created_at': datetime.now() - timedelta(hours=6)
        },
        {
            'title': '会员积分到账',
            'content': '恭喜您！您的最近一次飞行已获得500积分，当前总积分为2,350分。积分可用于兑换免费机票或升级服务。',
            'type': 'success',
            'created_at': datetime.now() - timedelta(hours=2)
        },
        {
            'title': '在线选座功能上线',
            'content': '好消息！蓝天航空在线选座功能现已正式上线。您可以在航班起飞前24小时为已确认的订单选择座位，让您的旅程更加舒适。',
            'type': 'info',
            'created_at': datetime.now() - timedelta(hours=1)
        }
    ]
    
    for notice in notices:
        notice_id = db.execute_insert(
            """INSERT INTO notices (title, content, type, created_at, is_active) 
               VALUES (%s, %s, %s, %s, %s)""",
            (notice['title'], notice['content'], notice['type'], notice['created_at'], 1)
        )
        print(f"通知创建成功，ID: {notice_id}")

def init_user_notices(user_id):
    """初始化用户通知关联数据"""
    print("正在初始化用户通知关联数据...")
    
    # 获取所有通知
    notices = db.execute_query("SELECT notice_id FROM notices WHERE is_active = 1")
    
    # 为测试用户创建一些已读通知
    read_notices = [1, 3]  # 第1个和第3个通知标记为已读
    
    for notice in notices:
        notice_id = notice['notice_id']
        is_read = notice_id in read_notices
        
        if is_read:
            db.execute_insert(
                "INSERT INTO user_notices (notice_id, user_id, read_at) VALUES (%s, %s, %s)",
                (notice_id, user_id, datetime.now())
            )
    
    print(f"用户通知关联数据创建完成")

def main():
    """主函数"""
    print("开始初始化数据库...")
    
    try:
        # 初始化测试用户
        user_id = init_test_user()
        
        # 初始化通知数据
        init_notices()
        
        # 初始化用户通知关联
        init_user_notices(user_id)
        
        print("数据库初始化完成！")
        print(f"测试账户: admin@example.com")
        print(f"测试密码: 123456")
        
    except Exception as e:
        print(f"初始化失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 