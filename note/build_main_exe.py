import os
import subprocess
import shutil

def build_fighter():
    print("🚀 正在打包核心战斗程序 (AutoFighter.exe)...")
    
    # PyInstaller 参数
    # -F: 单文件模式
    # -n: 输出文件名
    # -c: 显示控制台 (方便看日志)
    cmd = [
        'pyinstaller',
        '-F',                   # 打包成单个exe
        '-c',                   # 显示黑色命令行窗口 (如果要隐藏改为 -w)
        '-n', 'AutoFighter',    # exe名字
        '--clean',              # 清理缓存
        '--distpath', '.',      # 输出到当前目录，方便直接调试
        'src/main.py'           # 入口文件
    ]
    
    try:
        subprocess.check_call(cmd, shell=True)
        print("\n✅ AutoFighter.exe 打包完成！")
        
        # 清理生成的临时文件
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('AutoFighter.spec'):
            os.remove('AutoFighter.spec')
            
    except subprocess.CalledProcessError:
        print("\n❌ 打包失败，请检查错误信息。")

if __name__ == '__main__':
    build_fighter()