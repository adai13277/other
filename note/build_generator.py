import os
import subprocess
import shutil
import sys

def build_generator():
    print("🚀 正在打包 License 生成器 (LicenseGenerator.exe)...")
    
    # 检测关键依赖文件是否存在
    # 因为生成器严重依赖这两个文件，如果不存在打包会成功但无法运行
    required_files = ['license_validator.py', 'generate_license.py']
    missing = [f for f in required_files if not (os.path.exists(f) or os.path.exists(os.path.join('src', 'tools', f)))]
    
    if missing:
        print(f"\n⚠️  警告: 未找到依赖文件: {missing}")
        print("请确保 'license_validator.py' 和 'generate_license.py' 在当前目录或 'tools' 文件夹下。")
        print("否则生成的程序将无法正常计算密钥。")
        user_input = input("是否继续打包? (y/n): ")
        if user_input.lower() != 'y':
            return

    # PyInstaller 参数
    cmd = [
        'pyinstaller',
        '-F',                    # 单文件模式
        '-w',                    # 窗口模式 (无控制台)
        '-n', 'LicenseGenerator',# exe名字
        '--clean',               # 清理缓存
        '--distpath', '.',       # 输出到当前目录
        
        # 核心依赖：PyQt5 和 加密库
        '--hidden-import', 'PyQt5.sip',
        '--hidden-import', 'cryptography',
        
        # 将当前目录加入路径，防止找不到模块
        '--paths', '.', 
        
        'src/license_generator_gui.py' # 入口文件
    ]
    
    try:
        subprocess.check_call(cmd, shell=True)
        print("\n✅ LicenseGenerator.exe 打包完成！")
        
        # 清理临时文件
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('LicenseGenerator.spec'):
            os.remove('LicenseGenerator.spec')

    except subprocess.CalledProcessError:
        print("\n❌ 打包失败，请检查错误信息。")

if __name__ == '__main__':
    build_generator()