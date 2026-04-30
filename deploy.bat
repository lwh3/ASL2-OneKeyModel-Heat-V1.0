@echo off
REM LF精炼炉加热模型监控系统 - Windows部署脚本
REM Unified Deployment Script for Windows

echo ========================================
echo LF精炼炉加热模型监控系统 - 部署向导
echo ========================================
echo.

:menu
echo.
echo 请选择部署选项:
echo 1) 完整部署 (后端 + Vue3 + WPF)
echo 2) 仅部署后端
echo 3) 仅部署Vue3前端
echo 4) 仅构建WPF应用
echo 5) 启动后端服务
echo 6) 启动Vue3开发服务器
echo 7) 停止所有服务
echo 8) 退出
echo.

set /p choice="请输入选项 (1-8): "

if "%choice%"=="1" goto full_deploy
if "%choice%"=="2" goto deploy_backend
if "%choice%"=="3" goto deploy_vue3
if "%choice%"=="4" goto build_wpf
if "%choice%"=="5" goto start_backend
if "%choice%"=="6" goto start_vue3
if "%choice%"=="7" goto stop_services
if "%choice%"=="8" goto exit
goto menu

:full_deploy
call :deploy_backend
call :deploy_vue3
call :build_wpf
goto done

:deploy_backend
echo.
echo === 部署后端服务 ===
cd Backend
echo 安装Python依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: Python依赖安装失败
    pause
    exit /b 1
)
echo 后端部署完成
cd ..
goto :eof

:deploy_vue3
echo.
echo === 部署Vue3 WebUI ===
cd Frontend-Vue3
echo 安装Node.js依赖...
call npm install
if errorlevel 1 (
    echo 错误: Node.js依赖安装失败
    pause
    exit /b 1
)
echo 构建生产版本...
call npm run build
if errorlevel 1 (
    echo 错误: Vue3构建失败
    pause
    exit /b 1
)
echo Vue3前端构建完成
echo 构建文件位于: Frontend-Vue3\dist\
cd ..
goto :eof

:build_wpf
echo.
echo === 构建WPF Desktop应用 ===
cd Frontend-WPF\HeatModelMonitor
echo 还原.NET依赖...
dotnet restore
if errorlevel 1 (
    echo 错误: .NET依赖还原失败
    pause
    exit /b 1
)
echo 构建发布版本...
dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true
if errorlevel 1 (
    echo 错误: WPF构建失败
    pause
    exit /b 1
)
echo WPF应用构建完成
echo 可执行文件位于: Frontend-WPF\HeatModelMonitor\bin\Release\net10.0-windows\win-x64\publish\
cd ..\..
goto :eof

:start_backend
echo.
echo === 启动后端服务 ===
cd Backend
start "LF Backend" python web_app.py
echo 后端服务已启动
echo 访问: http://localhost:5000
cd ..
pause
goto menu

:start_vue3
echo.
echo === 启动Vue3开发服务器 ===
cd Frontend-Vue3
start "LF Vue3" npm run dev
echo Vue3服务已启动
echo 访问: http://localhost:3000
cd ..
pause
goto menu

:stop_services
echo.
echo === 停止所有服务 ===
taskkill /FI "WINDOWTITLE eq LF Backend*" /F 2>nul
taskkill /FI "WINDOWTITLE eq LF Vue3*" /F 2>nul
echo 所有服务已停止
pause
goto menu

:done
echo.
echo ========================================
echo 部署完成!
echo ========================================
pause
goto menu

:exit
echo 退出部署脚本
exit /b 0
