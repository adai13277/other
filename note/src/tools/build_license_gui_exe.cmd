@echo off
REM AutoFighter License Generator - PyInstaller 打包脚本
REM 需要先安装: pip install pyinstaller

cd /d %~dp0..

echo.
echo ============================================
echo  AutoFighter License Generator - EXE 打包
echo ============================================
echo.

REM 1. 检查 PyInstaller
echo [1/4] 检查 PyInstaller...
python -m pip list | findstr pyinstaller >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ 未安装 PyInstaller，正在安装...
    python -m pip install pyinstaller
)
echo ✅ PyInstaller 已就绪

REM 2. 清理旧的构建
echo.
echo [2/4] 清理旧的构建文件...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
echo ✅ 清理完成

REM 3. 打包
echo.
echo [3/4] 打包中 (这可能需要 1-2 分钟)...
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "LicenseGenerator" ^
    --add-data "tools\generate_license.py:tools" ^
    --add-data "private_key.pem:." ^
    tools\license_generator_gui.py

if errorlevel 1 (
    echo.
    echo ❌ 打包失败
    pause
    exit /b 1
)
echo ✅ 打包完成

REM 4. 结果提示
echo.
echo [4/4] 完成
echo.
echo ============================================
echo  ✅ License 生成器 EXE 已生成！
echo ============================================
echo.
echo 位置: dist\LicenseGenerator.exe
echo.
echo 可以直接发送给用户使用，无需安装 Python
echo.
pause
