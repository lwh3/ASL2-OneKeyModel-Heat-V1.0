#!/bin/bash

# LF精炼炉加热模型监控系统 - 统一部署脚本
# Unified Deployment Script for LF Heating Model System

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}LF精炼炉加热模型监控系统 - 部署向导${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查Python
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误: 未找到Python 3，请先安装Python 3.8或更高版本${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Python 3 已安装${NC}"
}

# 检查Node.js
check_nodejs() {
    if ! command -v node &> /dev/null; then
        echo -e "${YELLOW}警告: 未找到Node.js，Vue3前端将无法部署${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ Node.js 已安装${NC}"
    return 0
}

# 检查.NET
check_dotnet() {
    if ! command -v dotnet &> /dev/null; then
        echo -e "${YELLOW}警告: 未找到.NET SDK，WPF应用将无法构建${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ .NET SDK 已安装${NC}"
    return 0
}

# 部署后端
deploy_backend() {
    echo -e "\n${BLUE}=== 部署后端服务 ===${NC}"
    cd Backend

    echo -e "${YELLOW}安装Python依赖...${NC}"
    pip3 install -r requirements.txt

    echo -e "${GREEN}✓ 后端部署完成${NC}"
    cd ..
}

# 部署Vue3前端
deploy_vue3() {
    echo -e "\n${BLUE}=== 部署Vue3 WebUI ===${NC}"
    cd Frontend-Vue3

    echo -e "${YELLOW}安装Node.js依赖...${NC}"
    npm install

    echo -e "${YELLOW}构建生产版本...${NC}"
    npm run build

    echo -e "${GREEN}✓ Vue3前端构建完成${NC}"
    echo -e "${GREEN}  构建文件位于: Frontend-Vue3/dist/${NC}"
    cd ..
}

# 构建WPF应用
build_wpf() {
    echo -e "\n${BLUE}=== 构建WPF Desktop应用 ===${NC}"
    cd Frontend-WPF/HeatModelMonitor

    echo -e "${YELLOW}还原.NET依赖...${NC}"
    dotnet restore

    echo -e "${YELLOW}构建发布版本...${NC}"
    dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true

    echo -e "${GREEN}✓ WPF应用构建完成${NC}"
    echo -e "${GREEN}  可执行文件位于: Frontend-WPF/HeatModelMonitor/bin/Release/net10.0-windows/win-x64/publish/${NC}"
    cd ../..
}

# 启动服务
start_services() {
    echo -e "\n${BLUE}=== 启动服务 ===${NC}"

    case $1 in
        backend)
            echo -e "${YELLOW}启动后端服务...${NC}"
            cd Backend
            python3 web_app.py &
            echo $! > backend.pid
            echo -e "${GREEN}✓ 后端服务已启动 (PID: $(cat backend.pid))${NC}"
            echo -e "${GREEN}  访问: http://localhost:5000${NC}"
            cd ..
            ;;
        vue3)
            echo -e "${YELLOW}启动Vue3开发服务器...${NC}"
            cd Frontend-Vue3
            npm run dev &
            echo $! > vue3.pid
            echo -e "${GREEN}✓ Vue3服务已启动${NC}"
            echo -e "${GREEN}  访问: http://localhost:3000${NC}"
            cd ..
            ;;
        all)
            start_services backend
            start_services vue3
            ;;
    esac
}

# 停止服务
stop_services() {
    echo -e "\n${BLUE}=== 停止服务 ===${NC}"

    if [ -f Backend/backend.pid ]; then
        kill $(cat Backend/backend.pid) 2>/dev/null || true
        rm Backend/backend.pid
        echo -e "${GREEN}✓ 后端服务已停止${NC}"
    fi

    if [ -f Frontend-Vue3/vue3.pid ]; then
        kill $(cat Frontend-Vue3/vue3.pid) 2>/dev/null || true
        rm Frontend-Vue3/vue3.pid
        echo -e "${GREEN}✓ Vue3服务已停止${NC}"
    fi
}

# 主菜单
show_menu() {
    echo ""
    echo -e "${BLUE}请选择部署选项:${NC}"
    echo "1) 完整部署 (后端 + Vue3 + WPF)"
    echo "2) 仅部署后端"
    echo "3) 仅部署Vue3前端"
    echo "4) 仅构建WPF应用"
    echo "5) 启动后端服务"
    echo "6) 启动Vue3开发服务器"
    echo "7) 启动所有服务"
    echo "8) 停止所有服务"
    echo "9) 退出"
    echo ""
    read -p "请输入选项 (1-9): " choice

    case $choice in
        1)
            check_python
            deploy_backend
            if check_nodejs; then
                deploy_vue3
            fi
            if check_dotnet; then
                build_wpf
            fi
            ;;
        2)
            check_python
            deploy_backend
            ;;
        3)
            if check_nodejs; then
                deploy_vue3
            else
                echo -e "${RED}错误: 需要Node.js才能部署Vue3前端${NC}"
                exit 1
            fi
            ;;
        4)
            if check_dotnet; then
                build_wpf
            else
                echo -e "${RED}错误: 需要.NET SDK才能构建WPF应用${NC}"
                exit 1
            fi
            ;;
        5)
            start_services backend
            ;;
        6)
            start_services vue3
            ;;
        7)
            start_services all
            ;;
        8)
            stop_services
            ;;
        9)
            echo -e "${GREEN}退出部署脚本${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}无效选项${NC}"
            show_menu
            ;;
    esac
}

# 执行主菜单
show_menu

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}部署完成!${NC}"
echo -e "${GREEN}========================================${NC}"
