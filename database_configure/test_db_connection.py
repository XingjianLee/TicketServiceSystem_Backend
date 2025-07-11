import sys
import os
from ..app.core.database import db
from ..app.core.config import settings

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_connection():
    print("正在测试数据库连接...")
    print(f"数据库配置:")
    print(f"  主机: {settings.database_host}")
    print(f"  端口: {settings.database_port}")
    print(f"  用户: {settings.database_user}")
    print(f"  数据库: {settings.database_name}")

    try:
        # 测试连接
        with db.get_connection() as conn:
            print("✅ 数据库连接成功！")

            # 测试查询
            with conn.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                print(f"✅ MySQL 版本: {version['VERSION()']}")

                # 检查数据库是否存在
                cursor.execute("SHOW DATABASES LIKE %s", (settings.database_name,))
                db_exists = cursor.fetchone()
                if db_exists:
                    print(f"✅ 数据库 '{settings.database_name}' 存在")
                else:
                    print(f"❌ 数据库 '{settings.database_name}' 不存在")
                    return False

                # 检查表是否存在
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                table_names = [list(table.values())[0] for table in tables]
                print(f"✅ 数据库中的表: {', '.join(table_names) if table_names else '无'}")

                # 检查关键表
                required_tables = ['users', 'flights', 'orders', 'routes', 'aircraft']
                missing_tables = [table for table in required_tables if table not in table_names]

                if missing_tables:
                    print(f"⚠️  缺少以下表: {', '.join(missing_tables)}")
                    print("请运行 create_tables.sql 创建表结构")
                else:
                    print("✅ 所有必需的表都存在")

                # 检查数据
                if 'users' in table_names:
                    cursor.execute("SELECT COUNT(*) as count FROM users")
                    user_count = cursor.fetchone()
                    print(f"✅ 用户表中有 {user_count['count']} 条记录")

                if 'flights' in table_names:
                    cursor.execute("SELECT COUNT(*) as count FROM flights")
                    flight_count = cursor.fetchone()
                    print(f"✅ 航班表中有 {flight_count['count']} 条记录")

        return True

    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("数据库连接测试")
    print("=" * 50)

    success = test_connection()

    print("\n" + "=" * 50)
    if success:
        print("🎉 数据库连接测试通过！")
    else:
        print("❌ 数据库连接测试失败！")
    print("=" * 50)


if __name__ == "__main__":
    main()
