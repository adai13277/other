@echo off
REM 这是一个批处理文件，用于激活Conda环境并运行Python脚本
chcp 65001
echo 正在切换到批处理所在目录...
cd /d "%~dp0/src"

echo 正在激活Conda环境 'venv313'...
CALL conda activate venv313

echo 正在以交互模式运行 main.py...
echo -------------------------------------
python -i main.py
echo -------------------------------------

echo.
echo 程序已执行完毕。由于使用了 -i 参数，窗口将保持打开。
echo 您可以检查变量或进行其他操作。输入 exit() 并按回车可关闭此窗口。

REM 暂停命令在这里不是必须的，因为 python -i 已经阻止了窗口关闭。
REM 但如果您想无论如何都暂停，可以取消下面一行的注释。
REM pause