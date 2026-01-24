#!/usr/bin/env python3
"""
AutoFighter 配置编辑器打包脚本

使用 PyInstaller 将 config_editor_gui.py 打包成独立的 exe 文件
"""
import os
import sys
import PyInstaller.__main__
from pathlib import Path

# ===================== 配置参数 =====================
PROJECT_ROOT = Path(__file__).parent.parent  # 项目根目录
SRC_DIR = PROJECT_ROOT / "src"
CONFIG_EDITOR = SRC_DIR / "config_editor_gui.py"
BUILD_DIR = SRC_DIR / "build_editor"
DIST_DIR = SRC_DIR / "dist_editor"
OUTPUT_NAME = "AutoFighter_ConfigEditor"

# ===================== 打包数据 =====================
DATAS = [
    # (源路径, 目标路径)
    (str(SRC_DIR / "config.json"), "."),  # 配置文件
    (str(SRC_DIR / "action_help.json"), "."),  # 动作帮助文件
]

# ===================== 隐藏导入 =====================
HIDDENIMPORTS = [
    "license_validator",
    "PyQt5.QtCore",
    "PyQt5.QtGui",
    "PyQt5.QtWidgets",
]

def build_editor_exe():
    """打包 config_editor_gui.py 为 AutoFighter_ConfigEditor.exe"""
    
    print("\n" + "="*70)
    print("AutoFighter 配置编辑器打包")
    print("="*70)
    
    args = [
        str(CONFIG_EDITOR),  # 主文件
        "--onefile",  # 单文件输出
        f"--name={OUTPUT_NAME}",  # 输出名称
        f"--distpath={DIST_DIR}",  # 输出目录
        f"--buildpath={BUILD_DIR}",  # 构建目录
        "--windowed",  # GUI 模式（无控制台窗口）
        "--noconfirm",  # 无需确认覆盖
        "--clean",  # 清理临时文件
        "--icon=NONE",  # 暂不设置图标
    ]
    
    # 添加数据文件
    for src, dst in DATAS:
        args.append(f"--add-data={src}{os.pathsep}{dst}")
    
    # 添加隐藏导入
    for module in HIDDENIMPORTS:
        args.append(f"--hidden-import={module}")
    
    print(f"\n📦 打包配置:")
    print(f"  主文件: {CONFIG_EDITOR}")
    print(f"  输出: {OUTPUT_NAME}.exe")
    print(f"  输出目录: {DIST_DIR}")
    print(f"  数据文件: {len(DATAS)} 个")
    print(f"  隐藏导入: {len(HIDDENIMPORTS)} 个")
    
    print(f"\n🔨 开始打包...")
    try:
        PyInstaller.__main__.run(args)
        
        exe_path = DIST_DIR / f"{OUTPUT_NAME}.exe"
        if exe_path.exists():
            print(f"\n✅ 打包成功!")
            print(f"📍 输出路径: {exe_path}")
            print(f"📊 文件大小: {exe_path.stat().st_size / 1024 / 1024:.2f} MB")
            return True
        else:
            print(f"\n❌ 打包失败: 未找到输出文件")
            return False
            
    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("AutoFighter 配置编辑器 - 打包工具")
    print("="*70)
    
    # 检查依赖
    print("\n📋 检查依赖...")
    
    try:
        import PyInstaller
        print(f"✓ PyInstaller 已安装 (版本: {PyInstaller.__version__})")
    except ImportError:
        print("✗ PyInstaller 未安装")
        print("  请运行: pip install pyinstaller")
        return False
    
    try:
        import PyQt5
        print(f"✓ PyQt5 已安装")
    except ImportError:
        print("✗ PyQt5 未安装")
        print("  请运行: pip install PyQt5")
        return False
    
    # 检查主文件
    if not CONFIG_EDITOR.exists():
        print(f"✗ 配置编辑器文件不存在: {CONFIG_EDITOR}")
        return False
    print(f"✓ 配置编辑器文件存在: {CONFIG_EDITOR}")
    
    # 打包
    success = build_editor_exe()
    
    print("\n" + "="*70)
    if success:
        print("✅ 打包完成!")
        print("\n📌 使用说明:")
        print("1. AutoFighter_ConfigEditor.exe 可直接运行")
        print("2. 建议将其放在专门的目录中")
        print("3. 确保 config.json 和 action_help.json 在同一目录")
    else:
        print("❌ 打包失败，请检查错误信息")
    print("="*70 + "\n")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
