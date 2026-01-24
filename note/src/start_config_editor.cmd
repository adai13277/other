@echo off
REM =====================================================
REM AutoFighter 配置编辑器启动脚本
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
echo   AutoFighter 配置编辑器
echo ======================================================
echo.

REM 尝试启动编辑器 exe
if exist "AutoFighter_ConfigEditor.exe" (
    echo [INFO] 正在启动配置编辑器...
    echo [INFO] 位置: %SCRIPT_DIR%AutoFighter_ConfigEditor.exe
    echo.
    timeout /t 2 /nobreak
    
    REM 后台启动编辑器
    start "" "AutoFighter_ConfigEditor.exe"
    
    echo.
    echo [OK] 配置编辑器已启动！
    echo.
    
) else (
    echo.
    echo [WARNING] 未找到编辑器 exe，尝试使用 Python 脚本...
    echo.
    
    if exist "config_editor_gui.py" (
        python config_editor_gui.py
    ) else (
        echo [ERROR] 配置编辑器文件不存在！
        echo.
        echo [INFO] 解决方案：
        echo   1. 运行打包脚本: python build_all.py
        echo   2. 或使用: python build_editor_exe.py
        echo.
        echo 按任意键退出...
        pause > nul
    )
)

endlocal

