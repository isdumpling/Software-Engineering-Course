#!/bin/bash

echo "================================"
echo "智能课程助教聊天机器人 - 前端启动"
echo "================================"
echo ""

# 检查Node.js环境
echo "检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js，请先安装Node.js"
    echo "下载地址: https://nodejs.org/"
    exit 1
fi

echo "Node.js版本: $(node --version)"
echo ""

# 检查npm环境
echo "检查npm环境..."
if ! command -v npm &> /dev/null; then
    echo "错误: 未找到npm"
    exit 1
fi

echo "npm版本: $(npm --version)"
echo ""

# 检查依赖是否已安装
echo "检查依赖是否已安装..."
if [ ! -d "node_modules" ]; then
    echo "依赖未安装，正在安装..."
    npm install
    if [ $? -ne 0 ]; then
        echo "依赖安装失败，请检查网络连接"
        exit 1
    fi
else
    echo "依赖已安装"
fi

echo ""
echo "启动开发服务器..."
echo "项目将在 http://localhost:8080 启动"
echo "按 Ctrl+C 停止服务器"
echo ""

npm run serve