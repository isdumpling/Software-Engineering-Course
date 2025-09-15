#!/usr/bin/env python3
"""
数据库初始化脚本
运行此脚本来创建数据库和表
"""

import sys
import pymysql
from database import engine, Base
from config import settings
from models import User, ChatSession, ChatMessage, ResetToken

def create_database():
    """创建数据库（如果不存在）"""
    try:
        # 连接到MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ 数据库 '{settings.MYSQL_DATABASE}' 创建成功")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        return False
    
    return True

def create_tables():
    """创建所有表"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ 数据表创建成功")
        return True
    except Exception as e:
        print(f"❌ 创建数据表失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("智能课程助教聊天机器人 - 数据库初始化")
    print("=" * 50)
    
    # 显示配置信息
    print(f"📊 数据库配置:")
    print(f"   主机: {settings.MYSQL_HOST}")
    print(f"   端口: {settings.MYSQL_PORT}")
    print(f"   用户: {settings.MYSQL_USER}")
    print(f"   数据库: {settings.MYSQL_DATABASE}")
    print()
    
    # 创建数据库
    print("1️⃣ 创建数据库...")
    if not create_database():
        sys.exit(1)
    
    # 创建表
    print("\n2️⃣ 创建数据表...")
    if not create_tables():
        sys.exit(1)
    
    print("\n🎉 数据库初始化完成！")
    print("\n📝 创建的表包括:")
    print("   - users (用户表)")
    print("   - chat_sessions (聊天会话表)")
    print("   - chat_messages (聊天消息表)")
    print("   - reset_tokens (密码重置令牌表)")
    print("\n🚀 现在可以启动后端服务了！")

if __name__ == "__main__":
    main()