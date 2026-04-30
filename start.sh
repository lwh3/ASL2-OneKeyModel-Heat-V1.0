#!/bin/bash

# LF精炼炉加热模型 - 启动脚本 (Linux/Mac)
# ASL2-OneKeyModel-Heat-V1.0 Startup Script

echo "=========================================="
echo "LF精炼炉加热模型启动脚本"
echo "ASL2 OneKeyModel Heat V1.0"
echo "=========================================="
echo ""

# 切换到Backend目录
cd "$(dirname "$0")/Backend" || exit 1

# 检查Python是否安装
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null
then
    echo "错误: 未找到Python"
    echo "请先安装Python 3.8或更高版本"
    exit 1
fi

# 使用python3或python命令
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "使用Python: $($PYTHON_CMD --version)"
echo ""

# 检查依赖是否安装
echo "检查依赖..."
if ! $PYTHON_CMD -c "import flask" &> /dev/null; then
    echo "警告: 依赖未完全安装"
    echo "正在安装依赖..."
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误: 依赖安装失败"
        exit 1
    fi
fi

echo "依赖检查完成"
echo ""

# 创建必要的目录
mkdir -p logs
echo "已创建日志目录: logs/"
echo ""

# 询问启动模式
echo "请选择启动模式:"
echo "1. Web UI模式 (推荐) - 包含守护进程和Web界面"
echo "2. 守护进程模式 (仅后台服务，无Web界面)"
echo ""
read -p "请输入选项 (1/2，默认1): " mode
mode=${mode:-1}

if [ "$mode" = "1" ]; then
    echo ""
    echo "启动模式: Web UI"
    echo "访问地址: http://localhost:5000"
    echo ""
    echo "按 Ctrl+C 停止服务"
    echo "=========================================="
    echo ""

    # 启动Web UI
    $PYTHON_CMD web_app.py

elif [ "$mode" = "2" ]; then
    echo ""
    echo "启动模式: 守护进程"
    echo ""
    read -p "是否创建数据库表? (y/n，默认n): " create_tables
    create_tables=${create_tables:-n}

    if [ "$create_tables" = "y" ] || [ "$create_tables" = "Y" ]; then
        echo "将创建数据库表..."
        $PYTHON_CMD main.py --create-tables
    else
        $PYTHON_CMD main.py
    fi

else
    echo "无效的选项"
    exit 1
fi
