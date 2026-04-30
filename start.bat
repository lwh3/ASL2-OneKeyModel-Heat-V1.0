@echo off
REM LF精炼炉加热模型 - 启动脚本 (Windows)
REM ASL2-OneKeyModel-Heat-V1.0 Startup Script

echo ==========================================
echo LF精炼炉加热模型启动脚本
echo ASL2 OneKeyModel Heat V1.0
echo ==========================================
echo.

REM 切换到Backend目录
cd /d "%~dp0Backend"

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python
    echo 请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

python --version
echo.

REM 检查依赖是否安装
echo 检查依赖...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 依赖未完全安装
    echo 正在安装依赖...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

echo 依赖检查完成
echo.

REM 创建必要的目录
if not exist "logs" mkdir logs
echo 已创建日志目录: logs\
echo.

REM 询问启动模式
echo 请选择启动模式:
echo 1. Web UI模式 (推荐) - 包含守护进程和Web界面
echo 2. 守护进程模式 (仅后台服务，无Web界面)
echo.
set /p mode="请输入选项 (1/2，默认1): "
if "%mode%"=="" set mode=1

if "%mode%"=="1" (
    echo.
    echo 启动模式: Web UI
    echo 访问地址: http://localhost:5000
    echo.
    echo 按 Ctrl+C 停止服务
    echo ==========================================
    echo.

    REM 启动Web UI
    python web_app.py

) else if "%mode%"=="2" (
    echo.
    echo 启动模式: 守护进程
    echo.
    set /p create_tables="是否创建数据库表? (y/n，默认n): "
    if "%create_tables%"=="" set create_tables=n

    if /i "%create_tables%"=="y" (
        echo 将创建数据库表...
        python main.py --create-tables
    ) else (
        python main.py
    )

) else (
    echo 无效的选项
    pause
    exit /b 1
)

pause
