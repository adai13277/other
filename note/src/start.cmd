@echo off
REM =====================================================
REM AutoFighter 主程序启动脚本
REM =====================================================

setlocal enabledelayedexpansion
chcp 65001 > nul

REM 获取当前脚本所在目录
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM 输出欢迎信息
cls
echo.
echo ======================================================
echo   AutoFighter - 游戏自动化助手
echo ======================================================
echo.

REM 尝试启动 AutoFighter.exe
if exist "AutoFighter.exe" (
    echo [INFO] 正在启动主程序...
    echo [INFO] 位置: %SCRIPT_DIR%AutoFighter.exe
    echo.
    timeout /t 2 /nobreak
    
    REM 后台启动主程序
    start "" "AutoFighter.exe"
    
    echo.
    echo [OK] 主程序已启动！
    echo [INFO] 按任意键关闭此窗口...
    pause > nul
    
) else (
    echo.
    echo [ERROR] 错误：未找到 AutoFighter.exe
    echo.
    echo [INFO] 解决方案：
    echo   1. 运行打包脚本: python build_all.py
    echo   2. 或单独打包: python build_main_exe.py
    echo.
    echo 按任意键退出...
    pause > nul
)

endlocal