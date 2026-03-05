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
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=',
    'q','w','e','r','t','y',
    'a','s','d','f','g',
    'space', 'shift', 'ctrl', 
    'insert','delete',
    'home', 'end', 'pageup', 'pagedown'
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
                        'param_explanation': info.get('param_explanation', ''),
                        'param_types': self._get_param_types_from_json(info.get('default_args', [])),
                        'param_examples': self._get_param_examples_from_json(info.get('default_args', []))
                    }
            else:
                # 如果文件不存在，给个默认值防止报错，或者静默处理
                print(f"Warning: {help_path} 不存在")
                
        except Exception as e:
            print(f"加载action_help.json失败: {e}")
            # 如果JSON加载失败，尝试动态加载action_driver作为备用
            methods = self._load_action_help_from_action_driver()
        
        return methods
    
    def _load_action_help_from_json(self):
        """从action_help.json加载攻击模式信息（备用方案）"""
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


    def _get_param_types_from_json(self, default_args):
        """从默认参数推断参数类型"""
        param_types = []
        for arg in default_args:
            if isinstance(arg, bool):
                param_types.append('bool')
            elif isinstance(arg, int):
                param_types.append('int')
            elif isinstance(arg, float):
                param_types.append('float')
            elif isinstance(arg, str):
                param_types.append('str')
            else:
                param_types.append('any')
        return param_types

    def _get_param_examples_from_json(self, default_args):
        """从默认参数生成参数示例"""
        examples = []
        for i, arg in enumerate(default_args):
            examples.append(str(arg))
        return examples

    def _load_action_help_from_action_driver(self):
        """从action_driver动态加载攻击模式信息（备用方案）"""
        methods = {}
        try:
            # 动态导入action_driver模块
            import sys
            sys.path.insert(0, self.base_dir)
            from action_driver import ActionDriver
            
            # 先从action_help.json获取已配置的函数列表
            help_path = os.path.join(self.base_dir, 'action_help.json')
            configured_functions = set()
            
            if os.path.exists(help_path):
                with open(help_path, 'r', encoding='utf-8') as f:
                    help_data = json.load(f)
                configured_functions = set(help_data.get('actions', {}).keys())
            
            # 获取ActionDriver类的所有方法，但只返回在action_help.json中配置的函数
            for method_name in dir(ActionDriver):
                if not method_name.startswith('_') and callable(getattr(ActionDriver, method_name)):
                    # 只加载在action_help.json中有配置的函数
                    if method_name not in configured_functions:
                        continue
                    
                    method = getattr(ActionDriver, method_name)
                    
                    # 获取装饰器添加的描述
                    desc = getattr(method, '_action_desc', '无描述')
                    
                    # 获取函数签名和文档字符串
                    import inspect
                    try:
                        # 获取函数签名
                        sig = inspect.signature(method)
                        params = list(sig.parameters.keys())[1:]  # 跳过self参数
                        
                        # 获取文档字符串作为详细说明
                        doc = inspect.getdoc(method) or '无参数说明'
                        
                        methods[method_name] = {
                            'desc': desc,
                            'params': params,
                            'default_args': [],
                            'param_explanation': doc,
                            'param_types': [],
                            'param_examples': []
                        }
                    except Exception as e:
                        print(f"获取方法 {method_name} 信息失败: {e}")
                        # 使用基本信息
                        methods[method_name] = {
                            'desc': desc,
                            'params': [],
                            'default_args': [],
                            'param_explanation': '无法获取详细信息',
                            'param_types': [],
                            'param_examples': []
                        }
                        
        except Exception as e:
            print(f"动态加载action_driver失败: {e}")
        
        return methods

    def initUI(self):
        self.setWindowTitle('⚙️ AutoFighter 配置编辑器 v2.2')
        self.setGeometry(100, 100, 1300, 900)
        
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
        在配置编辑器同级目录下查找 AutoFighter.exe 文件并启动
        """
        # 获取配置编辑器所在目录（即 AutoFighter.exe 应该在的目录）
        current_dir = self.base_dir
        
        # 在同级目录下查找 AutoFighter.exe
        target_path = os.path.join(current_dir, "AutoFighter.exe")
        
        if not os.path.exists(target_path):
            QMessageBox.warning(
                self, 
                "❌ 启动失败", 
                "未找到配置编辑器同级目录下的 AutoFighter.exe\n\n"
                f"查找路径: {target_path}\n\n"
                "请确保 AutoFighter.exe 文件存在于配置编辑器同级目录中"
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
                cwd=current_dir,  # 在配置编辑器目录下启动
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
            
            # 构建详细的参数说明
            param_info = self._build_param_info(func_name, info)
            self.params_hint.setText(param_info)
        else:
            self.attack_mode_desc.setText('自定义或未知函数')
            self.params_hint.setText('')

    def _build_param_info(self, func_name, info):
        """构建详细的参数说明信息"""
        lines = []
        
        # 函数签名
        params = info.get('params', [])
        if params:
            param_list = ', '.join(params)
            lines.append(f"函数签名: {func_name}({param_list})")
        else:
            lines.append(f"函数签名: {func_name}()")
        
        # 函数描述（从文档字符串）
        doc = info.get('param_explanation', '')
        if doc and doc != '无参数说明':
            lines.append(f"\n详细说明:\n{doc}")
        
        return '\n'.join(lines)

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
        
        scroll.setMinimumWidth(800)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        group_style = """
            QGroupBox {
                font-weight: bold;
                border: 1px solid #AAA;
                border-radius: 5px;
                margin-top: 12px; 
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                left: 10px;
            }
        """

        # 硬直Buff区域
        stun_group = QGroupBox('💥 硬直Buff配置（有抬手动作）')
        stun_group.setStyleSheet(group_style)
        stun_group.setMinimumWidth(750)
        stun_group.setToolTip('有抬手动作的技能，如攻击技能、瞬移技能等，需要暂停移动来释放')
        stun_layout = QFormLayout()

        self.stun_buff_rows = []
        
        # 创建 7 个硬直Buff槽位
        for i in range(7):
            h_layout = QHBoxLayout()
            
            # 1. 启用开关
            checkbox = QCheckBox(f'硬直Buff {i+1}')
            # checkbox.setFixedWidth(140)
            
            # 2. 按键选择 (ComboBox, 可编辑)
            key_combo = QComboBox()
            key_combo.setEditable(True) # 允许输入自定义按键
            key_combo.setFixedWidth(120)
            key_combo.addItems(PYAUTOGUI_KEYS) # 添加预设按键
            key_combo.setCurrentText("")
            key_combo.setEnabled(False)

            # 3. 间隔时间
            spinbox = QSpinBox()
            spinbox.setRange(0, 9999)
            spinbox.setValue(0)
            spinbox.setSuffix(' 秒')
            spinbox.setEnabled(False)

            # 4. 【新增】开局等待复选框
            delay_check = QCheckBox("5秒后施放")
            delay_check.setToolTip("勾选: 开局等待5秒后立即释放一次\n不勾选: 开局进入冷却，等待一个间隔后才释放")
            delay_check.setEnabled(False)
            
            # 逻辑联动 (修改 lambda 传入 delay_check)
            checkbox.stateChanged.connect(
                lambda state, k=key_combo, s=spinbox, d=delay_check: self._on_buff_row_toggled(state, k, s, d)
            )

            h_layout.addWidget(checkbox)
            h_layout.addWidget(QLabel("按键:"))
            h_layout.addWidget(key_combo)
            h_layout.addWidget(QLabel("间隔:"))
            h_layout.addWidget(spinbox)
            h_layout.addWidget(delay_check) # 添加到布局
            h_layout.addStretch()
            
            stun_layout.addRow(h_layout)
            
            self.stun_buff_rows.append({
                'check': checkbox,
                'key': key_combo,
                'time': spinbox,
                'delay': delay_check, # 存入引用
                'type': 'stun'
            })

        stun_group.setLayout(stun_layout)
        scroll_layout.addWidget(stun_group)

        # 非硬直Buff区域
        non_stun_group = QGroupBox('🧪 非硬直Buff配置（无抬手动作，如药水药丸之类）')
        non_stun_group.setStyleSheet(group_style)
        non_stun_group.setMinimumWidth(750)
        non_stun_group.setToolTip('无抬手动作的消耗品，如药水、药丸等，可以边移动边使用')
        non_stun_layout = QFormLayout()

        self.non_stun_buff_rows = []
        
        # 创建 6 个非硬直Buff槽位
        for i in range(6):
            h_layout = QHBoxLayout()
            
            # 1. 启用开关
            checkbox = QCheckBox(f'非硬直Buff {i+1}')
            # checkbox.setFixedWidth(120)
            
            # 2. 按键选择 (ComboBox, 可编辑)
            key_combo = QComboBox()
            key_combo.setEditable(True) # 允许输入自定义按键
            key_combo.setFixedWidth(120)
            key_combo.addItems(PYAUTOGUI_KEYS) # 添加预设按键
            key_combo.setCurrentText("")
            key_combo.setEnabled(False)

            # 3. 间隔时间
            spinbox = QSpinBox()
            spinbox.setRange(0, 9999)
            spinbox.setValue(0)
            spinbox.setSuffix(' 秒')
            spinbox.setEnabled(False)

            # 【新增】
            delay_check = QCheckBox("5秒后施放")
            delay_check.setToolTip("勾选: 开局等待5秒后立即释放一次\n不勾选: 开局进入冷却，等待一个间隔后才释放")
            delay_check.setEnabled(False)
            
            checkbox.stateChanged.connect(
                lambda state, k=key_combo, s=spinbox, d=delay_check: self._on_buff_row_toggled(state, k, s, d)
            )

            h_layout.addWidget(checkbox)
            h_layout.addWidget(QLabel("按键:"))
            h_layout.addWidget(key_combo)
            h_layout.addWidget(QLabel("间隔:"))
            h_layout.addWidget(spinbox)
            h_layout.addWidget(delay_check)
            h_layout.addStretch()
            
            non_stun_layout.addRow(h_layout)
            
            self.non_stun_buff_rows.append({
                'check': checkbox,
                'key': key_combo,
                'time': spinbox,
                'delay': delay_check, # 存入引用
                'type': 'non_stun'
            })

        non_stun_group.setLayout(non_stun_layout)
        scroll_layout.addWidget(non_stun_group)
        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        layout.addWidget(QLabel('💡 提示：按键支持下拉选择(如 shift, space, f1) 或 直接输入字母。取消勾选即禁用该槽位。'))
        widget.setLayout(layout)
        return widget

    def _on_stun_buff_toggled(self, state, key_combo, spinbox):
        """处理硬直Buff的启用/禁用状态变化"""
        enabled = (state == 2)
        key_combo.setEnabled(enabled)
        spinbox.setEnabled(enabled)
        if enabled and spinbox.value() == 0:
            spinbox.setValue(180) # 默认给个数值方便编辑

    def _on_non_stun_buff_toggled(self, state, key_combo, spinbox):
        """处理非硬直Buff的启用/禁用状态变化"""
        enabled = (state == 2)
        key_combo.setEnabled(enabled)
        spinbox.setEnabled(enabled)
        if enabled and spinbox.value() == 0:
            spinbox.setValue(180) # 默认给个数值方便编辑

    def _on_buff_row_toggled(self, state, key_combo, spinbox, delay_check):
        """统一处理Buff行的启用状态"""
        enabled = (state == 2)
        key_combo.setEnabled(enabled)
        spinbox.setEnabled(enabled)
        delay_check.setEnabled(enabled) # 启用/禁用新加的复选框
        
        if enabled and spinbox.value() == 0:
            spinbox.setValue(180)

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
            
            # 配置加载完成时不自动验证License，只在手动点击按钮时验证
            # 清除之前的验证状态
            self.license_status.setText('未验证')
            self.license_status.setStyleSheet("color: black;")
            self.license_info.clear()
            
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
        for row in self.stun_buff_rows + self.non_stun_buff_rows:
            row['check'].setChecked(False)
            row['key'].setCurrentText('')
            row['time'].setValue(0)
            row['delay'].setChecked(False)
            
        # 填充数据：先填充硬直buff，再填充非硬直buff
        stun_count = 0
        non_stun_count = 0
        
        for sc in shortcuts:
            key = sc.get('key', '')
            
            # ============ 修改开始 ============ 
            # 强制将 interval 转换为整数。先转float再转int是为了兼容字符串"1.0"或浮点数1.5的情况
            try:
                raw_val = sc.get('interval', -1)
                interval = int(float(raw_val))
            except (ValueError, TypeError):
                interval = 0
            # ============ 修改结束 ============

            buff_type = sc.get('type', 'non_stun')  # 默认为非硬直buff
            # 【新增】读取 delay_enabled，默认为 False
            is_delay = sc.get('delay_enabled', False) 
            
            if interval != -1:
                if buff_type == 'stun' and stun_count < len(self.stun_buff_rows):
                    # 填充硬直buff
                    row = self.stun_buff_rows[stun_count]
                    stun_count += 1
                elif buff_type == 'non_stun' and non_stun_count < len(self.non_stun_buff_rows):
                    # 填充非硬直buff
                    row = self.non_stun_buff_rows[non_stun_count]
                    non_stun_count += 1
                else:
                    # 超出槽位限制，跳过
                    continue
                
                row['check'].setChecked(True)
                row['key'].setCurrentText(key)
                row['time'].setValue(interval) # 现在这里传入的一定是 int
                row['delay'].setChecked(is_delay) # 【新增】设置复选框状态

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
            
            # 先收集硬直buff
            for row in self.stun_buff_rows:
                if row['check'].isChecked():
                    key = row['key'].currentText().strip()
                    interval = row['time'].value()
                    # 【新增】获取复选框状态
                    delay_enabled = row['delay'].isChecked()
                    
                    if key: 
                        new_shortcuts.append({
                            'key': key,
                            'interval': interval,
                            'type': 'stun',
                            'delay_enabled': delay_enabled # 【新增】保存到JSON
                        })
            
            # 再收集非硬直buff (同理)
            for row in self.non_stun_buff_rows:
                if row['check'].isChecked():
                    key = row['key'].currentText().strip()
                    interval = row['time'].value()
                    delay_enabled = row['delay'].isChecked()
                    
                    if key: 
                        new_shortcuts.append({
                            'key': key,
                            'interval': interval,
                            'type': 'non_stun',
                            'delay_enabled': delay_enabled # 【新增】
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
        
        # 恢复license key，但不自动验证
        if current_license_key:
            self.license_key_input.setText(current_license_key)
            # 清除之前的验证状态，只在手动点击按钮时验证
            self.license_status.setText('未验证')
            self.license_status.setStyleSheet("color: black;")
            self.license_info.clear()

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