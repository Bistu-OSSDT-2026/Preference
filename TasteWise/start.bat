@echo off
chcp 65001 >nul
title TasteWise 食谱推荐系统

echo ============================================
echo    🍜 TasteWise - 食谱推荐系统
echo ============================================
echo.

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [❌] 未检测到 Python，请先安装 Python 3.10+
    echo     下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查/创建虚拟环境
if not exist ".venv\Scripts\activate.bat" (
    echo [📦] 正在创建虚拟环境...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [❌] 虚拟环境创建失败
        pause
        exit /b 1
    )
)

:: 激活虚拟环境
call .venv\Scripts\activate.bat

:: 检查依赖
pip show streamlit >nul 2>&1
if %errorlevel% neq 0 (
    echo [📥] 正在安装依赖（首次运行需要几分钟）...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [❌] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [✅] 环境就绪，正在启动 TasteWise...
echo.
echo [💡] 浏览器将自动打开 http://localhost:8501
echo [🛑] 关闭本窗口即可停止应用
echo.
echo ============================================

:: 启动应用
streamlit run app.py

pause
