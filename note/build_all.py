#!/usr/bin/env python3
"""
AutoFighter 完整打包脚本

一键将主程序和配置编辑器打包成 exe
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

# ===================== 项目路径 =====================
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
OUTPUT_DIR = PROJECT_ROOT / "AutoFighter_Release"

def print_header(title):
    """打印标题"""
    print("\n" + "="*70)
    print(title.center(70))
    print("="*70)

def print_section(title):
    """打印小标题"""
    print(f"\n📌 {title}")
    print("-" * 70)

def check_dependencies():
    """检查依赖"""
    print_section("检查依赖")
    
    deps = {
        "PyInstaller": "pip install pyinstaller",
        "PyQt5": "pip install PyQt5",
        "cryptography": "pip install cryptography",
    }
    
    all_ok = True
    for module, install_cmd in deps.items():
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module} 未安装")
            print(f"  执行: {install_cmd}")
            all_ok = False
    
    return all_ok

def check_source_files():
    """检查源文件"""
    print_section("检查源文件")
    
    required_files = [
        SRC_DIR / "main.py",
        SRC_DIR / "config_editor_gui.py",
        SRC_DIR / "config.json",
        SRC_DIR / "action_help.json",
        SRC_DIR / "license_validator.py",
        SRC_DIR / "auto_fighter.py",
        SRC_DIR / "action_driver.py",
    ]
    
    all_ok = True
    for file in required_files:
        if file.exists():
            print(f"✓ {file.relative_to(PROJECT_ROOT)}")
        else:
            print(f"✗ {file.relative_to(PROJECT_ROOT)} 不存在")
            all_ok = False
    
    return all_ok

def build_main_exe():
    """打包主程序"""
    print_section("打包主程序 (AutoFighter.exe)")
    
    script = PROJECT_ROOT / "build_main_exe.py"
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=300  # 5 分钟超时
        )
        
        print(result.stdout)
        if result.returncode != 0:
            print("错误输出:")
            print(result.stderr)
            return False
        
        return True
    except subprocess.TimeoutExpired:
        print("❌ 打包超时")
        return False
    except Exception as e:
        print(f"❌ 打包失败: {e}")
        return False

def build_editor_exe():
    """打包配置编辑器"""
    print_section("打包配置编辑器 (AutoFighter_ConfigEditor.exe)")
    
    script = PROJECT_ROOT / "build_editor_exe.py"
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=300  # 5 分钟超时
        )
        
        print(result.stdout)
        if result.returncode != 0:
            print("错误输出:")
            print(result.stderr)
            return False
        
        return True
    except subprocess.TimeoutExpired:
        print("❌ 打包超时")
        return False
    except Exception as e:
        print(f"❌ 打包失败: {e}")
        return False

def copy_executables_to_src():
    """将生成的 exe 复制到 src 目录"""
    print_section("整合可执行文件")
    
    main_exe = SRC_DIR / "dist" / "AutoFighter.exe"
    editor_exe = SRC_DIR / "dist_editor" / "AutoFighter_ConfigEditor.exe"
    
    src_main = SRC_DIR / "AutoFighter.exe"
    src_editor = SRC_DIR / "AutoFighter_ConfigEditor.exe"
    
    success = True
    
    if main_exe.exists():
        shutil.copy2(main_exe, src_main)
        print(f"✓ 已复制: AutoFighter.exe")
    else:
        print(f"✗ 未找到: {main_exe}")
        success = False
    
    if editor_exe.exists():
        shutil.copy2(editor_exe, src_editor)
        print(f"✓ 已复制: AutoFighter_ConfigEditor.exe")
    else:
        print(f"✗ 未找到: {editor_exe}")
        success = False
    
    return success

def create_release_package():
    """创建发布包"""
    print_section("创建发布包")
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    files_to_copy = [
        (SRC_DIR / "AutoFighter.exe", "AutoFighter.exe"),
        (SRC_DIR / "AutoFighter_ConfigEditor.exe", "AutoFighter_ConfigEditor.exe"),
        (SRC_DIR / "config.json", "config.json"),
        (SRC_DIR / "action_help.json", "action_help.json"),
        (SRC_DIR / "start.cmd", "start.cmd"),
        (SRC_DIR / "start_config_editor.cmd", "start_config_editor.cmd"),
    ]
    
    success = True
    for src, dst_name in files_to_copy:
        if src.exists():
            dst = OUTPUT_DIR / dst_name
            shutil.copy2(src, dst)
            print(f"✓ {dst_name}")
        else:
            print(f"✗ {src.name} 不存在，跳过")
    
    # 创建 README
    readme = OUTPUT_DIR / "README.md"
    if not readme.exists():
        readme.write_text("""# AutoFighter - 游戏自动化助手

## 使用说明

### 方式 1: 使用编辑器启动
```
双击 AutoFighter_ConfigEditor.exe
└─ 在编辑器中配置并保存
└─ 点击"开启辅助"按钮
└─ 开始自动化
```

### 方式 2: 直接启动主程序
```
双击 AutoFighter.exe
└─ 加载配置文件
└─ 开始自动化
```

### 方式 3: 使用批处理文件
```
start.cmd                       # 启动主程序
start_config_editor.cmd         # 启动配置编辑器
```

## 文件说明

- **AutoFighter.exe** - 主程序
- **AutoFighter_ConfigEditor.exe** - 配置编辑器
- **config.json** - 配置文件（编辑器会修改）
- **action_help.json** - 动作帮助信息（只读）

## 常见问题

### Q: 如何修改配置?
A: 运行 AutoFighter_ConfigEditor.exe，在图形界面中编辑配置

### Q: 如何自定义攻击模式?
A: 在编辑器的"基本配置"标签页中选择或输入函数名和参数

### Q: License 怎样获取?
A: 在编辑器的"License"标签页中获取本机机器码，
   然后将机器码发送给管理员生成 License

## 技术支持

有问题请查看日志文件: auto_fighter.log

---

版本: 2.0
最后更新: 2026-01-24
""")
        print("✓ README.md")
    
    return success

def create_batch_launchers():
    """创建批处理启动文件"""
    print_section("创建启动文件")
    
    # 启动主程序的批处理
    start_main = SRC_DIR / "start.cmd"
    if not start_main.exists():
        start_main.write_text("""@echo off
cd /d "%~dp0"
echo 正在启动 AutoFighter...
AutoFighter.exe
pause
""")
        print("✓ start.cmd")
    
    # 启动编辑器的批处理
    start_editor = SRC_DIR / "start_config_editor.cmd"
    if not start_editor.exists():
        start_editor.write_text("""@echo off
cd /d "%~dp0"
echo 正在启动 AutoFighter 配置编辑器...
AutoFighter_ConfigEditor.exe
pause
""")
        print("✓ start_config_editor.cmd")

def main():
    print_header("AutoFighter 完整打包工具")
    
    print("\n本脚本将:")
    print("  1. 检查所有依赖")
    print("  2. 打包主程序为 AutoFighter.exe")
    print("  3. 打包编辑器为 AutoFighter_ConfigEditor.exe")
    print("  4. 创建发布包")
    print("  5. 准备启动脚本")
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请先安装所需的包")
        return False
    
    # 检查源文件
    if not check_source_files():
        print("\n❌ 源文件检查失败")
        return False
    
    # 打包主程序
    if not build_main_exe():
        print("\n❌ 主程序打包失败")
        return False
    
    # 打包编辑器
    if not build_editor_exe():
        print("\n❌ 编辑器打包失败")
        return False
    
    # 复制可执行文件到 src
    if not copy_executables_to_src():
        print("\n⚠️ 部分文件复制失败，继续...")
    
    # 创建发布包
    if not create_release_package():
        print("\n⚠️ 发布包创建失败")
    
    # 创建启动脚本
    create_batch_launchers()
    
    # 完成
    print_header("✅ 打包完成")
    
    print("\n📍 生成的文件:")
    print(f"  主程序: {SRC_DIR / 'AutoFighter.exe'}")
    print(f"  编辑器: {SRC_DIR / 'AutoFighter_ConfigEditor.exe'}")
    print(f"  发布包: {OUTPUT_DIR}")
    
    print("\n🚀 下一步:")
    print("  1. 双击 AutoFighter_ConfigEditor.exe 打开编辑器")
    print("  2. 配置参数并保存")
    print("  3. 点击'开启辅助'启动主程序")
    print("  或者直接双击 AutoFighter.exe 运行")
    
    print("\n💡 提示:")
    print("  - 首次运行可能需要一些时间加载")
    print("  - 如遇到错误，查看 auto_fighter.log 文件")
    
    print("\n" + "="*70 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断打包")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
