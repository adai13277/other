import sys
import json
import os
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QCheckBox, QPushButton, QTextEdit,
    QMessageBox, QGroupBox, QFormLayout, QComboBox, QDoubleSpinBox, 
    QScrollArea, QTabWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QClipboard
from tools.license_validator import LicenseValidator

# ================= 隐藏CMD窗口配置 =================
HIDE_CONSOLE_WINDOW = True  # 设置为 True 则隐藏cmd窗口，False 则显示

# ================= 公钥（硬编码）=================
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAp+qN2nLs9rqI3C623SLf
PTGUEhvzwDu3z1an4wAvpHPbAt+06oQwTxJZ5IXOx4Id29jQxexd7hMdLYFUw8s1
1dxgei8n/SlVSxfj6sNqj1p37YfUkVFpy88fOPTFmZ1GYkbhsh67ybAwVqaJJUS9
DTS5Fd2ET88zk8gHZ9fo4nNPvkPX+gTotGK93yyck2BO2JB5OxXq9ZYc6ROUqZC3
pmLQ4Hyb+B5DXTo/yDBLoPX/nBGc0UvJIRBs/Q0NlMKIF/5lw+8vtZNE568xg2Vi
P76rQvsDyu+9xc69ovkNEdku2zONlr+/jw77CHFD3R/LMJvzh+zyLSULA+wx6ScL
+QIDAQAB
-----END PUBLIC KEY-----"""

# ================= 支持的按键列表 =================
PYAUTOGUI_KEYS = [
    'space', 'shift', 'ctrl', 
    'insert',
    'home', 'end', 'pageup', 'pagedown',
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 
    # ... (other keys)
]

class ConfigEditorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # 修改路径逻辑以兼容打包后的路径
        if getattr(sys, 'frozen', False):
            # 如果是打包后的 exe，路径是可执行文件所在的目录
            self.base_dir = os.path.dirname(sys.executable)
        else:
            # 如果是脚本运行，路径是文件所在的目录
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.config_path = os.path.join(self.base_dir, 'config.json')
        self.current_config = {}
        
        # 从JSON文件加载action帮助信息
        self.action_methods = self._load_action_help()
        
        self.validator = LicenseValidator(PUBLIC_KEY, is_path=False)
        self.buff_ui_rows = [] # 存储Buff行的UI控件引用
        
        self.initUI()
        self.load_config()

    def _load_action_help(self):
        """从action_help.json加载攻击模式信息"""
        methods = {}
        try:
            # 使用 self.base_dir 确保读取的是 EXE 同级目录下的文件
            help_path = os.path.join(self.base_dir, 'action_help.json')
            
            if os.path.exists(help_path):
                with open(help_path, 'r', encoding='utf-8') as f:
                    help_data = json.load(f)
                
                actions = help_data.get('actions', {})
                for name, info in actions.items():
                    methods[name] = {
                        'desc': info.get('desc', ''),
                        'params': info.get('params', []),
                        'default_args': info.get('default_args', []),
                        'param_explanation': info.get('param_explanation', '')
                    }
            else:
                # 如果文件不存在，给个默认值防止报错，或者静默处理
                print(f"Warning: {help_path} 不存在")
                
        except Exception as e:
            print(f"加载action_help.json失败: {e}")
        
        return methods

    def initUI(self):
        self.setWindowTitle('⚙️ AutoFighter 配置编辑器 v2.2')
        self.setGeometry(100, 100, 1200, 900)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()

        # ==================== 顶部区域：标题 + 启动按钮 ====================
        top_bar = QHBoxLayout()
        
        title_label = QLabel('⚙️ AutoFighter 配置编辑器')
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # 新增：启动辅助按钮
        self.run_btn = QPushButton('🚀 开启辅助')
        self.run_btn.setStyleSheet("""
            QPushButton { background-color: #E91E63; color: white; font-weight: bold; padding: 8px 15px; border-radius: 5px; }
            QPushButton:hover { background-color: #D81B60; }
        """)
        self.run_btn.clicked.connect(self.run_external_program)
        
        top_bar.addWidget(title_label)
        top_bar.addStretch()
        top_bar.addWidget(self.run_btn)
        
        main_layout.addLayout(top_bar)

        # ==================== 标签页 ====================
        tabs = QTabWidget()
        tabs.addTab(self.create_basic_tab(), '🎯 基本配置')
        tabs.addTab(self.create_license_tab(), '🔐 License')
        tabs.addTab(self.create_buffs_tab(), '⚡ Buff 配置')
        main_layout.addWidget(tabs)

        # ==================== 底部按钮 ====================
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton('💾 保存配置')
        self.save_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; border-radius: 5px; font-size: 11pt; } QPushButton:hover { background-color: #45a049; }")
        self.save_btn.clicked.connect(self.save_config)
        
        self.reload_btn = QPushButton('🔄 重新加载')
        self.reload_btn.clicked.connect(self.load_config)
        self.reload_btn.setMinimumHeight(40)
        
        self.reset_btn = QPushButton('🔃 恢复默认')
        self.reset_btn.clicked.connect(self.reset_to_default)
        self.reset_btn.setMinimumHeight(40)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.reload_btn)
        button_layout.addWidget(self.reset_btn)
        main_layout.addLayout(button_layout)

        central.setLayout(main_layout)

    def run_external_program(self):
        """
        运行 AutoFighter 主程序
        只查找根目录下的 AutoFighter.exe 文件并启动
        """
        # 获取项目根目录（config_editor_gui.py 的上一级目录）
        current_dir = self.base_dir
        parent_dir = os.path.dirname(current_dir)  # 项目根目录
        
        # 只查找根目录下的 AutoFighter.exe
        target_path = os.path.join(parent_dir, "AutoFighter.exe")
        
        if not os.path.exists(target_path):
            QMessageBox.warning(
                self, 
                "❌ 启动失败", 
                "未找到根目录下的 AutoFighter.exe\n\n"
                f"查找路径: {target_path}\n\n"
                "请确保 AutoFighter.exe 文件存在于项目根目录中"
            )
            return
        
        try:
            # 保存当前配置（避免运行时配置丢失）
            self.save_config()
            
            # 显示正在启动的消息
            print(f"[INFO] 正在启动: AutoFighter.exe")
            print(f"[INFO] 程序路径: {target_path}")
            
            # 启动程序 - 不隐藏cmd窗口
            subprocess.Popen(
                [target_path],
                cwd=parent_dir,  # 在根目录下启动
                shell=False
            )
            
            print(f"[INFO] 已启动: AutoFighter.exe")
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "❌ 启动失败", 
                f"无法启动程序:\n{str(e)}\n\n"
                f"尝试的文件: {target_path}"
            )

    def create_basic_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # 配置选择
        select_group = QGroupBox('📝 选择配置方案')
        select_layout = QFormLayout()
        self.config_combo = QComboBox()
        self.config_combo.currentTextChanged.connect(self.on_config_changed)
        self.config_desc = QLineEdit()
        select_layout.addRow('配置编号:', self.config_combo)
        select_layout.addRow('方案描述:', self.config_desc)
        select_group.setLayout(select_layout)
        layout.addWidget(select_group)

        # 攻击模式
        attack_group = QGroupBox('🎯 攻击模式配置')
        attack_layout = QFormLayout()

        self.attack_mode_combo = QComboBox()
        self.attack_mode_combo.addItem('', '') # 空白选项
        
        # 填充带有描述的攻击模式（从JSON加载）
        for name, info in self.action_methods.items():
            # 显示格式：loop_att (左右往返移动...)
            display_text = f"{name} ({info['desc']})"
            # addItem(text, userData) -> userData 存储真实的函数名
            self.attack_mode_combo.addItem(display_text, name)

        self.attack_mode_combo.currentIndexChanged.connect(self.on_attack_mode_changed)
        attack_layout.addRow('攻击模式(选择):', self.attack_mode_combo)

        # 函数名称输入框
        self.func_name_input = QLineEdit()
        self.func_name_input.setPlaceholderText('此处显示选中的函数名，也可手动修改')
        self.func_name_input.textChanged.connect(self._on_func_name_text_changed)
        attack_layout.addRow('函数名称(编辑):', self.func_name_input)

        # 模式说明
        self.attack_mode_desc = QLabel('')
        self.attack_mode_desc.setStyleSheet("color: #666; font-size: 10pt;")
        self.attack_mode_desc.setWordWrap(True)
        attack_layout.addRow('模式说明:', self.attack_mode_desc)

        # 参数提示（新增参数解析）
        self.params_hint = QLabel('')
        self.params_hint.setStyleSheet("color: #ff9800; font-size: 9pt;")
        self.params_hint.setWordWrap(True)
        attack_layout.addRow('参数说明:', self.params_hint)

        # 函数参数输入框
        self.params_input = QTextEdit()
        self.params_input.setPlaceholderText('例如: ["a", 2, 0.5]')
        self.params_input.setMinimumHeight(60)
        attack_layout.addRow('函数参数:', self.params_input)

        attack_group.setLayout(attack_layout)
        layout.addWidget(attack_group)
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _on_func_name_text_changed(self, text):
        """当手动修改函数名文本框时，尝试更新描述和参数说明"""
        func_name = text.strip()
        if func_name and func_name in self.action_methods:
            info = self.action_methods[func_name]
            self.attack_mode_desc.setText(info['desc'])
            self.params_hint.setText(info.get('param_explanation', ''))
        else:
            self.attack_mode_desc.setText('自定义或未知函数')
            self.params_hint.setText('')

    def create_license_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        license_group = QGroupBox('🔐 License 配置')
        license_layout = QFormLayout()

        self.license_key_input = QTextEdit()
        self.license_key_input.setMinimumHeight(100)
        self.license_key_input.setPlaceholderText("在此处粘贴 License Key")
        license_layout.addRow('License Key:', self.license_key_input)

        # 按钮区域：验证 + 获取机器码 + 粘贴验证
        btn_layout = QHBoxLayout()
        
        self.verify_license_btn = QPushButton('🔍 验证 License')
        self.verify_license_btn.clicked.connect(self.verify_license)
        self.verify_license_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 5px;")
        
        self.machine_code_btn = QPushButton('💻 获取本机机器码')
        self.machine_code_btn.clicked.connect(self.show_machine_code)
        self.machine_code_btn.setStyleSheet("padding: 5px;")
        
        self.paste_verify_btn = QPushButton('📋 粘贴并验证')
        self.paste_verify_btn.clicked.connect(self.paste_and_verify_license)
        self.paste_verify_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
        
        btn_layout.addWidget(self.verify_license_btn)
        btn_layout.addWidget(self.machine_code_btn)
        btn_layout.addWidget(self.paste_verify_btn)
        btn_layout.addStretch()
        
        license_layout.addRow('', btn_layout)

        self.license_status = QLabel('未验证')
        self.license_info = QTextEdit()
        self.license_info.setReadOnly(True)
        self.license_info.setMinimumHeight(100)
        license_layout.addRow('验证状态:', self.license_status)
        license_layout.addRow('密钥信息:', self.license_info)

        license_group.setLayout(license_layout)
        layout.addWidget(license_group)
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_buffs_tab(self):
        """创建 Buff 配置标签页（支持任意按键下拉选择）"""
        widget = QWidget()
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        buffs_group = QGroupBox('⚡ Buff 与 按键映射配置')
        buffs_layout = QFormLayout()

        self.buff_ui_rows = []
        
        # 创建 10 个通用的配置槽位
        for i in range(10):
            h_layout = QHBoxLayout()
            
            # 1. 启用开关
            checkbox = QCheckBox(f'Buff {i+1}')
            checkbox.setFixedWidth(80)
            
            # 2. 按键选择 (ComboBox, 可编辑)
            key_combo = QComboBox()
            key_combo.setEditable(True) # 允许输入自定义按键
            key_combo.setFixedWidth(120)
            key_combo.addItems(PYAUTOGUI_KEYS) # 添加预设按键
            key_combo.setCurrentText("")
            key_combo.setEnabled(False)

            # 3. 间隔时间
            spinbox = QDoubleSpinBox()
            spinbox.setRange(0, 9999)
            spinbox.setValue(0)
            spinbox.setSingleStep(0.1)
            spinbox.setSuffix(' 秒')
            spinbox.setEnabled(False)
            
            # 逻辑联动
            checkbox.stateChanged.connect(
                lambda state, k=key_combo, s=spinbox: self._on_buff_row_toggled(state, k, s)
            )

            h_layout.addWidget(checkbox)
            h_layout.addWidget(QLabel("按键:"))
            h_layout.addWidget(key_combo)
            h_layout.addWidget(QLabel("间隔:"))
            h_layout.addWidget(spinbox)
            h_layout.addStretch()
            
            buffs_layout.addRow(h_layout)
            
            self.buff_ui_rows.append({
                'check': checkbox,
                'key': key_combo,
                'time': spinbox
            })

        buffs_group.setLayout(buffs_layout)
        scroll_layout.addWidget(buffs_group)
        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        layout.addWidget(QLabel('💡 提示：按键支持下拉选择(如 shift, space, f1) 或 直接输入字母。取消勾选即禁用该槽位。'))
        widget.setLayout(layout)
        return widget

    def _on_buff_row_toggled(self, state, key_combo, spinbox):
        enabled = (state == 2)
        key_combo.setEnabled(enabled)
        spinbox.setEnabled(enabled)
        if enabled and spinbox.value() == 0:
            spinbox.setValue(180) # 默认给个数值方便编辑

    def load_config(self, is_startup=False):
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.current_config = json.load(f)
            
            # License
            self.license_key_input.setText(self.current_config.get('license', {}).get('key', ''))
            
            # Configs List
            configs = self.current_config.get('configs', {})
            self.config_combo.blockSignals(True)
            self.config_combo.clear()
            self.config_combo.addItems(list(configs.keys()))
            self.config_combo.blockSignals(False)
            
            # Select Current Config
            use_config = self.current_config.get('use_config', '1')
            if use_config in configs:
                self.config_combo.setCurrentText(use_config)
            elif configs:
                self.config_combo.setCurrentText(list(configs.keys())[0])

            self.on_config_changed() # 刷新详细界面
            
            if self.license_key_input.toPlainText().strip():
                self._verify_license_silent()
            
        except Exception as e:
            QMessageBox.warning(self, '⚠️ 错误', f'加载失败: {e}')

    def on_config_changed(self):
        config_num = self.config_combo.currentText()
        if not config_num: return
        
        config = self.current_config.get('configs', {}).get(config_num, {})
        
        # 1. 描述
        self.config_desc.setText(config.get('_desc', ''))
        
        # 2. 攻击模式
        action_seq = config.get('action_sequence', [])
        if action_seq:
            func_name = action_seq[0].get('function', '')
            args = action_seq[0].get('args', [])
            
            # 设置函数名文本框
            self.func_name_input.setText(func_name)
            
            # 屏蔽下拉框信号，防止 setCurrentIndex 触发 on_attack_mode_changed
            self.attack_mode_combo.blockSignals(True)
            index = self.attack_mode_combo.findData(func_name)
            if index >= 0:
                self.attack_mode_combo.setCurrentIndex(index)
            else:
                self.attack_mode_combo.setCurrentIndex(0)
            self.attack_mode_combo.blockSignals(False)
            
            self.params_input.setText(json.dumps(args, ensure_ascii=False))
        else:
            self.attack_mode_combo.setCurrentIndex(0)
            self.func_name_input.clear()
            self.params_input.clear()
            
        # 3. Buff 配置 (加载到槽位)
        shortcuts = config.get('SHORTCUTS', [])
        
        # 先清空所有槽位
        for row in self.buff_ui_rows:
            row['check'].setChecked(False)
            row['key'].setCurrentText('')
            row['time'].setValue(0)
            
        # 填充数据
        for i, sc in enumerate(shortcuts):
            if i >= len(self.buff_ui_rows): break 
            
            key = sc.get('key', '')
            interval = sc.get('interval', -1)
            
            if interval != -1:
                row = self.buff_ui_rows[i]
                row['check'].setChecked(True)
                row['key'].setCurrentText(key)
                row['time'].setValue(float(interval))

    def on_attack_mode_changed(self):
        """当下拉框选择变化时，更新函数名和参数"""
        func_name = self.attack_mode_combo.currentData()
        
        if func_name:
            # 将下拉框选中的值填入文本框
            self.func_name_input.setText(func_name)
            
            # 获取默认参数
            if func_name in self.action_methods:
                default_args = self.action_methods[func_name].get('default_args', [])
                self.params_input.setText(json.dumps(default_args, ensure_ascii=False))
        else:
            self.func_name_input.clear()
            self.params_input.clear()

    def save_config(self):
        try:
            config_num = self.config_combo.currentText()
            if not config_num: return
            
            # 保存 License
            license_key = self.license_key_input.toPlainText().strip()
            self.current_config['license']['key'] = license_key
            self.current_config['use_config'] = config_num
            
            # 准备 config 对象
            if config_num not in self.current_config.get('configs', {}):
                self.current_config.setdefault('configs', {})[config_num] = {}
            
            cfg = self.current_config['configs'][config_num]
            cfg['_desc'] = self.config_desc.text()
            
            # 读取手动编辑的函数名
            func_name = self.func_name_input.text().strip()
            
            if func_name:
                try:
                    args_str = self.params_input.toPlainText().strip()
                    args = json.loads(args_str) if args_str else []
                    cfg['action_sequence'] = [{'function': func_name, 'args': args}]
                except json.JSONDecodeError:
                    QMessageBox.warning(self, '格式错误', '参数必须是有效的 JSON 数组')
                    return
            
            # 保存 Buff (从 UI 槽位收集)
            new_shortcuts = []
            for row in self.buff_ui_rows:
                if row['check'].isChecked():
                    key = row['key'].currentText().strip()
                    interval = row['time'].value()
                    
                    if key: 
                        new_shortcuts.append({
                            'key': key,
                            'interval': interval
                        })
            
            cfg['SHORTCUTS'] = new_shortcuts
            
            # 写入文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_config, f, indent=2, ensure_ascii=False)
                
            QMessageBox.information(self, '✅ 成功', '配置已保存')
            
        except Exception as e:
            QMessageBox.critical(self, '错误', str(e))

    def verify_license(self):
        key = self.license_key_input.toPlainText().strip()
        if not key: return
        
        # 获取机器码用于显示
        machine_code = self._get_machine_code()
        
        try:
            # 验证密钥
            res = self.validator.verify(key)

            if res.get('valid'):
                self.license_status.setText('✅ 验证成功')
                self.license_status.setStyleSheet("color: green; font-weight: bold;")
                
                # 构建详细信息
                info_lines = []
                info_lines.append(f"验证状态: ✅ 有效")
                
                # 显示有效期（具体到分钟）
                expired_at = res.get('expired_at', '未知')
                info_lines.append(f"有效期至: {expired_at}")
                
                # 显示设备绑定状态
                require_binding = res.get('require_device_binding', True)
                if require_binding:
                    info_lines.append(f"设备绑定: ✅ 已启用（本机设备）")
                else:
                    info_lines.append(f"设备绑定: ⚠️ 未启用（任意设备可用）")
                
                # 显示本机信息
                info_lines.append(f"本机指纹: {machine_code}")
                
                # 显示验证消息
                if res.get('message'):
                    info_lines.append(f"消息: {res.get('message')}")
                
                self.license_info.setText('\n'.join(info_lines))
            else:
                self.license_status.setText('❌ 验证失败')
                self.license_status.setStyleSheet("color: red; font-weight: bold;")
                
                # 构建错误信息（包含调试信息）
                info_text = res.get('message', '未知错误')
                
                # 如果有额外的有效期信息
                expired_at = res.get('expired_at')
                if expired_at:
                    info_text += f"\n\n密钥有效期: {expired_at}"
                
                # 添加本机指纹信息
                info_text += f"\n\n本机指纹: {machine_code}"
                
                self.license_info.setText(info_text)
        except Exception as e:
            self.license_status.setText('❌ 异常错误')
            self.license_status.setStyleSheet("color: red;")
            self.license_info.setText(f"异常: {str(e)}\n\n本机指纹: {machine_code}")

    def _verify_license_silent(self):
        key = self.license_key_input.toPlainText().strip()
        if not key: return
        try:
            res = self.validator.verify(key)
            
            if res.get('valid'):
                self.license_status.setText('✅ 验证成功')
                self.license_status.setStyleSheet("color: green; font-weight: bold;")
                
                # 构建详细信息
                info_lines = []
                info_lines.append(f"验证状态: ✅ 有效")
                info_lines.append(f"有效期至: {res.get('expired_at', '未知')}")
                
                require_binding = res.get('require_device_binding', True)
                if require_binding:
                    info_lines.append(f"设备绑定: ✅ 已启用")
                else:
                    info_lines.append(f"设备绑定: ⚠️ 未启用")
                
                self.license_info.setText('\n'.join(info_lines))
        except: 
            pass

    def show_machine_code(self):
        """显示并复制机器码"""
        code = self.validator.get_machine_fingerprint()
        clipboard = QApplication.clipboard()
        clipboard.setText(code)
        QMessageBox.information(self, "本机机器码", f"机器码: {code}\n\n(已自动复制到剪贴板)")

    def _get_machine_code(self):
        """
        获取本机机器码（使用统一的验证器逻辑）
        确保与 License 验证时使用的机器码一致
        """
        return self.validator.get_machine_fingerprint()

    def reset_to_default(self):
        # 保存当前的license key
        current_license_key = self.license_key_input.toPlainText().strip()
        
        # 重新加载配置文件（恢复默认）
        self.load_config()
        
        # 恢复license key
        if current_license_key:
            self.license_key_input.setText(current_license_key)
            self._verify_license_silent()

    def paste_and_verify_license(self):
        """从剪贴板粘贴License Key并执行验证"""
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        
        if not text:
            QMessageBox.warning(self, '⚠️ 提示', '剪贴板中没有内容')
            return
        
        # 将剪贴板内容填入输入框
        self.license_key_input.setText(text)
        
        # 执行验证逻辑
        self.verify_license()

def main():
    # 隐藏cmd窗口（仅Windows）
    if HIDE_CONSOLE_WINDOW and sys.platform == 'win32':
        try:
            import ctypes
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 0)
        except:
            pass
    
    app = QApplication(sys.argv)
    window = ConfigEditorGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()