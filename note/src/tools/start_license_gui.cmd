@echo off
REM AutoFighter License Generator GUI - Windows 快速启动脚本
REM 使用方式: 双击此文件或在命令行运行

cd /d %~dp0

REM 启动 GUI
echo.
echo 🚀 启动 License 生成器...
echo.

python license_generator_gui.py

if errorlevel 1 (
    echo.
    echo ❌ 程序出错
    echo.
    pause
    exit /b 1
)
