#!/bin/bash

echo "===================================================="
echo "智能课程助教聊天机器人 - 后端服务启动 (Linux/Mac)"
echo "===================================================="
echo ""

# 检查Python环境
echo "检查Python环境..."
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "错误: 未找到Python，请先安装Python 3.8+"
    exit 1
fi

# 优先使用python3
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo "Python版本: $($PYTHON_CMD --version)"
echo ""

# 检查虚拟环境
if [ -n "$VIRTUAL_ENV" ]; then
    echo "当前虚拟环境: $VIRTUAL_ENV"
else
    echo "警告: 建议在虚拟环境中运行"
    echo "可以使用: python3 -m venv venv 创建虚拟环境"
    echo "然后运行: source venv/bin/activate 激活虚拟环境"
fi
echo ""

# 检查依赖
echo "检查依赖是否已安装..."
if ! $PYTHON_CMD -c "import fastapi, uvicorn, sqlalchemy, pymysql" &> /dev/null; then
    echo "依赖未安装，正在安装..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "依赖安装失败，请检查网络连接"
        exit 1
    fi
else
    echo "依赖已安装"
fi

echo ""
echo "启动后端服务..."
echo "服务地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"  
echo "按 Ctrl+C 停止服务"
echo ""

$PYTHON_CMD start.py