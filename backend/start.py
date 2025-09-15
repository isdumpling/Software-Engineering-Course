#!/usr/bin/env python3
"""
后端服务启动脚本
"""

import subprocess
import sys
import os

def check_requirements():
    """检查依赖是否已安装"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pymysql
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_database_connection():
    """检查数据库连接"""
    try:
        from database import engine
        connection = engine.connect()
        connection.close()
        print("✅ 数据库连接正常")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("请检查MySQL服务是否运行，并确认config.py中的数据库配置")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("智能课程助教聊天机器人 - 后端服务启动")
    print("=" * 50)
    
    # 检查依赖
    print("1️⃣ 检查依赖...")
    if not check_requirements():
        sys.exit(1)
    
    # 检查数据库连接
    print("\n2️⃣ 检查数据库连接...")
    if not check_database_connection():
        print("\n💡 提示: 如果是首次运行，请先执行以下步骤:")
        print("   1. 确保MySQL服务已启动")
        print("   2. 修改config.py中的数据库密码")
        print("   3. 运行: python init_db.py")
        sys.exit(1)
    
    # 启动服务
    print("\n3️⃣ 启动后端服务...")
    print("🚀 服务将在 http://localhost:8000 启动")
    print("📖 API文档地址: http://localhost:8000/docs")
    print("⏹️  按 Ctrl+C 停止服务")
    print("-" * 50)
    
    try:
        # 启动uvicorn服务
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 服务已停止")

if __name__ == "__main__":
    main()