import os
import subprocess
import shutil

def build_editor():
    print("🚀 正在打包配置编辑器 (ConfigEditor.exe)...")
    
    # PyInstaller 参数
    # -F: 单文件模式
    # -w: 窗口模式 (无控制台)
    # --hidden-import: 强制引入可能丢失的库
    cmd = [
        'pyinstaller',
        '-F',                   # 打包成单个exe
        '-w',                   # 隐藏黑框，纯图形界面
        '-n', '极速枫林(Maple Rush)',   # exe名字
        '--clean',
        '--distpath', '.',      # 输出到当前目录
        
        # 强制引入 PyQt5 相关模块，防止打包后报错
        '--hidden-import', 'PyQt5.sip',
        
        'src/config_editor_gui.py'  # 入口文件
    ]
    
    try:
        subprocess.check_call(cmd, shell=True)
        print("\n✅ ConfigEditor.exe 打包完成！")
        
        # 清理生成的临时文件
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('ConfigEditor.spec'):
            os.remove('ConfigEditor.spec')

    except subprocess.CalledProcessError:
        print("\n❌ 打包失败，请检查错误信息。")

if __name__ == '__main__':
    build_editor()