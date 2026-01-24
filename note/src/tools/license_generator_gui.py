"""
AutoFighter License Generator GUI
为小白用户提供友好的许可证生成界面
"""

import sys
import datetime
from pathlib import Path
import os

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QCheckBox, QPushButton, QTextEdit,
    QMessageBox, QGroupBox, QFormLayout, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# ================= 引用验证器逻辑 =================
# 假设 license_validator.py 在同一目录下，或已在 PYTHONPATH 中
try:
    from license_validator import LicenseValidator
except ImportError:
    # 如果找不到，提供一个占位符以防 GUI 崩溃（实际部署时应确保文件存在）
    class LicenseValidator:
        @staticmethod
        def get_machine_fingerprint():
            return "ERROR-VALIDATOR-NOT-FOUND"

# ================= 私钥（硬编码）=================
PRIVATE_KEY = (
    "-----BEGIN PRIVATE KEY-----\n"
    "MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCn6o3acuz2uojc\n"
    "LrbdIt89MZQSG/PAO7fPVqfjAC+kc9sC37TqhDBPElnkhc7Hgh3b2NDF7F3uEx0t\n"
    "gVTDyzXV3GB6Lyf9KVVLF+Pqw2qPWnfth9SRUWnLzx849MWZnUZiRuGyHrvJsDBW\n"
    "poklRL0NNLkV3YRPzzOTyAdn1+jic0++Q9f6BOi0Yr3fLJyTYE7YkHk7Fer1lhzp\n"
    "E5SpkLemYtDgfJv4HkNdOj/IMEug9f+cEZzRS8khEGz9DQ2UwogX/mXD7y+1k0Tn\n"
    "rzGDZWI/vqtC+wPK773Fzr2i+Q0R2S7bM42Wv7+PDvsIcUPdH8swm/OH7PItJQsD\n"
    "7DHpJwv5AgMBAAECggEAAYvPgEUVIst1nA0CqldNgp9JfsyXlyJMCO9CSGNcACUA\n"
    "WmhfBQn9D0lUhXebv3ejZaVIMAspk6begQ82QNkTtvmnWl12fiZqiBbuLN8qRMVZ\n"
    "CKY6yJcp+BJOHKSyVuQ25CV4PNiuf+B5sKtdZJ5Oqe4dmZKXcVji0tfha5ODHzMO\n"
    "4L9Fp9PW1fwmc9Lpxs7FzVy389dQEsTrIhgcWF+bXNirQfbCzfr2Jtx1+72gI9z+\n"
    "Tkm1+UgYLolbQITgXKAEOnKTKOc1N/nNV0fduYEYCXjqCwX3Ok2EnRowal9UABDD\n"
    "PO56UPumsOijnzqG8A7UQur074cr7ZZary43YgX85QKBgQDlh8Zt4m9CdI3u4VdC\n"
    "02NueJ+o2Yc4MWXHC1I/iyfZO71z7z+m+g5PjH4xCzlWgEAm+JGS1dcWBCZO4pPt\n"
    "227EpU24jEWjgRCDHBvnfvCjLa6jwhbk+YkOMeaoQkIGnE1ZCeZwc4UI8w3HngpM\n"
    "A9k99ro/O/p4Kjw/iq6lolnQhQKBgQC7R8xiGHpH9F384fnrNWoME50F2dHDNnqo\n"
    "tmO1w7V9erCEvfvJrrmWWTQCmsSm/WaB9KtDRwDGGuz2+pSUXVe6gxXPL6h6VLNo\n"
    "pq+Pxd/o71bOHF3fiV59w8z3wwhGwOedhmsbiswLHH2HYkdVx23/Iee0pHr4G/I+\n"
    "9Gog6LMB5QKBgQCQGF/7JhdA+hkMqYz1l+2pMbLR9tYL8f76KWJWIA9BMl7qhH1K\n"
    "X1tSl1m1gl1Zr6QWkyAYtYSU/r/p8BZ8UbDFZR1YyT8CuYjbNm9SMn/xgUFM7xEe\n"
    "aIWhUrSCVy5KJh/s0OlJGUygZK327oF6XUQpwVYFUqsYezNdlLu1oimOXQKBgQCW\n"
    "Ruqt3E5i5qd0gC/2mQnbXvGk/D/hkRmjv5cLB1vesFBsc7ZTA61QA4xEesRJ6xQS\n"
    "O64hchwg2wJCvJf05WG7++vIMMnUP5sm4noFuBYP592TzhdVg/kamb8jIJDHlYtF\n"
    "T9MqapmIYPgpZqcvIbQWAbLXtRQneuVLtvxiI9dgMQKBgDaCiSUtIqZj9F1zScQI\n"
    "cnc5+VjEdopbhzlrn7wIouVxaD9+u/5C84OqGpnsPxy5oWmrze4ZurM1tFnuedlJ\n"
    "8ZNHoEtA3iP/TQqcFfaVHRyyVA/13hVqBrCeGhQ+zx32o+VhGXo+9GFUMCIQz/ir\n"
    "U0EGw/rPIyfpQt6p0SXIKYKj\n"
    "-----END PRIVATE KEY-----"
)

# 导入生成逻辑
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from tools.generate_license import generate_license, set_private_key
    set_private_key(PRIVATE_KEY)
except ImportError:
    print("Warning: 未找到 tools.generate_license，使用模拟生成模式")
    def generate_license(device_fingerprint, days_valid, hours_valid, minutes_valid, require_device_binding):
        return f"MOCK-LICENSE-{device_fingerprint}-D{days_valid}H{hours_valid}M{minutes_valid}"
    def set_private_key(key):
        pass

class LicenseGeneratorGUI(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.current_license = "" 
        self.initUI()
        self.check_keys()

    # 原有的 get_machine_code 静态方法已删除，改用 LicenseValidator.get_machine_fingerprint

    def initUI(self):
        """初始化界面"""
        self.setWindowTitle('🔐 AutoFighter License 生成器')
        self.resize(900, 900) 
        
        font = QFont("Microsoft YaHei", 10)
        self.setFont(font)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()

        # ==================== 标题区域 ====================
        title_label = QLabel('🔐 AutoFighter License 生成工具')
        title_font = QFont("Microsoft YaHei", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        main_layout.addSpacing(15)

        # ==================== 输入表单区域 ====================
        form_group = QGroupBox('📝 参数配置')
        form_layout = QFormLayout()
        form_layout.setSpacing(20)

        # 1. 获取本机机器码按钮
        get_code_layout = QHBoxLayout()
        self.get_code_btn = QPushButton('🖥️ 获取本机机器码并绑定')
        self.get_code_btn.setMinimumHeight(50)
        self.get_code_btn.setMinimumWidth(200)
        self.get_code_btn.clicked.connect(self.get_and_copy_machine_code)
        self.get_code_btn.setCursor(Qt.PointingHandCursor)
        self.get_code_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                font-size: 12pt;
            }
            QPushButton:hover { background-color: #1565C0; }
        """)
        get_code_layout.addWidget(self.get_code_btn)
        get_code_layout.addStretch()
        form_layout.addRow('设备指纹:', get_code_layout)

        # 2. 用户机器码输入框
        machine_id_layout = QHBoxLayout()
        self.machine_id_input = QLineEdit()
        self.machine_id_input.setPlaceholderText('例如: WIN-XXXXXXXXXXXX 或 粘贴自定义机器码')
        self.machine_id_input.setMinimumHeight(35)
        self.machine_id_input.setEnabled(False)
        
        self.paste_btn = QPushButton('📋 粘贴')
        self.paste_btn.setMinimumHeight(35)
        self.paste_btn.setMinimumWidth(80)
        self.paste_btn.clicked.connect(self.paste_machine_id)
        self.paste_btn.setEnabled(False)

        machine_id_layout.addWidget(self.machine_id_input)
        machine_id_layout.addWidget(self.paste_btn)
        
        form_layout.addRow('用户机器码:', machine_id_layout)

        # 3. 有效期配置
        time_input_layout = QHBoxLayout()
        
        def create_time_spinbox(max_val, default=0):
            sb = QSpinBox()
            sb.setRange(0, max_val)
            sb.setValue(default)
            sb.setMinimumHeight(35)
            sb.setMinimumWidth(80)
            sb.setAlignment(Qt.AlignCenter)
            sb.setStyleSheet("""
                QSpinBox { font-size: 11pt; font-weight: bold; }
                QSpinBox::up-button, QSpinBox::down-button { width: 20px; }
            """)
            return sb

        self.days_spinbox = create_time_spinbox(7, 1)
        self.hours_spinbox = create_time_spinbox(23, 0)
        self.minutes_spinbox = create_time_spinbox(59, 0)
        
        time_input_layout.addWidget(self.days_spinbox)
        time_input_layout.addWidget(QLabel('天'))
        time_input_layout.addSpacing(10)
        time_input_layout.addWidget(self.hours_spinbox)
        time_input_layout.addWidget(QLabel('小时'))
        time_input_layout.addSpacing(10)
        time_input_layout.addWidget(self.minutes_spinbox)
        time_input_layout.addWidget(QLabel('分钟'))
        time_input_layout.addStretch()
        
        form_layout.addRow('有效期时长:', time_input_layout)

        # 快速选择按钮
        quick_btn_layout = QHBoxLayout()
        quick_btn_layout.setSpacing(15)
        
        quick_options = [("1天", 1), ("3天", 3), ("7天", 7)]
        
        for label, days in quick_options:
            btn = QPushButton(label)
            btn.setMinimumHeight(45)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0; 
                    border: 1px solid #ccc; 
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 11pt;
                }
                QPushButton:hover { background-color: #e0e0e0; border-color: #aaa; }
                QPushButton:pressed { background-color: #d0d0d0; }
            """)
            btn.clicked.connect(lambda checked, d=days: self._set_period(d, 0, 0))
            quick_btn_layout.addWidget(btn)
            
        form_layout.addRow('', quick_btn_layout)

        # 4. 安全策略
        device_binding_layout = QHBoxLayout()
        self.device_binding_checkbox = QCheckBox('强制绑定设备指纹')
        self.device_binding_checkbox.setChecked(False)
        self.device_binding_checkbox.setMinimumHeight(30)
        self.device_binding_checkbox.setStyleSheet("QCheckBox { font-size: 11pt; }")
        self.device_binding_checkbox.stateChanged.connect(self.on_device_binding_changed)
        
        device_binding_layout.addWidget(self.device_binding_checkbox)
        form_layout.addRow('安全策略:', device_binding_layout)

        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)

        # ==================== 生成按钮区域 ====================
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 15, 0, 15)
        
        self.generate_btn = QPushButton('🔑 生成 License Key')
        self.generate_btn.setMinimumHeight(55)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                font-size: 14pt;
            }
            QPushButton:hover { background-color: #1084E3; }
            QPushButton:pressed { background-color: #006CC1; }
            QPushButton:disabled { background-color: #CCCCCC; }
        """)
        self.generate_btn.clicked.connect(self.generate_license)
        
        self.reset_btn = QPushButton('重置')
        self.reset_btn.setFixedSize(80, 55)
        self.reset_btn.setStyleSheet("font-size: 11pt;")
        self.reset_btn.clicked.connect(self.reset_form)
        
        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(self.reset_btn)
        main_layout.addLayout(button_layout)

        # ==================== 结果显示区域 ====================
        result_group = QGroupBox('生成结果')
        result_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText('点击上方按钮生成密钥...')
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(500)
        self.result_text.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace; 
                font-size: 11pt;
                background-color: #FAFAFA;
                border: 1px solid #DDD;
                padding: 5px;
            }
        """)
        result_layout.addWidget(self.result_text)
        
        result_btn_layout = QHBoxLayout()
        
        self.copy_btn = QPushButton('📋 复制 Key')
        self.copy_btn.setMinimumHeight(45)
        self.copy_btn.setStyleSheet("font-size: 11pt; font-weight: bold;")
        self.copy_btn.clicked.connect(self.copy_key_to_clipboard)
        self.copy_btn.setEnabled(False)
        
        self.save_btn = QPushButton('💾 保存到文件...')
        self.save_btn.setMinimumHeight(45)
        self.save_btn.setStyleSheet("font-size: 11pt;")
        self.save_btn.clicked.connect(self.save_to_file)
        self.save_btn.setEnabled(False)
        
        result_btn_layout.addWidget(self.copy_btn)
        result_btn_layout.addWidget(self.save_btn)
        result_layout.addLayout(result_btn_layout)
        
        self.info_label = QLabel('就绪')
        self.info_label.setStyleSheet("color: #666; font-size: 9pt; margin-top: 5px;")
        result_layout.addWidget(self.info_label)
        
        result_group.setLayout(result_layout)
        main_layout.addWidget(result_group)

        central.setLayout(main_layout)

    def check_keys(self):
        try:
            if PRIVATE_KEY:
                self.info_label.setText("✅ 私钥已就绪")
        except Exception:
            pass

    def _set_period(self, days, hours, minutes):
        self.days_spinbox.setValue(days)
        self.hours_spinbox.setValue(hours)
        self.minutes_spinbox.setValue(minutes)

    def paste_machine_id(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            self.machine_id_input.setText(text)

    def get_and_copy_machine_code(self):
        """调用 Validator 获取机器码并复制到剪贴板"""
        try:
            # 修改处：直接调用 LicenseValidator 的静态方法
            machine_code = LicenseValidator.get_machine_fingerprint()
            
            QApplication.clipboard().setText(machine_code)
            self.info_label.setText(f"✅ 机器码已复制: {machine_code}")
            
            # 如果开启了绑定，直接填入
            if self.device_binding_checkbox.isChecked():
                self.machine_id_input.setText(machine_code)

            QMessageBox.information(
                self, '成功', 
                f'本机机器码已复制到剪贴板\n\n{machine_code}\n\n'
                '启用"强制绑定设备指纹"后可直接使用'
            )
        except Exception as e:
            QMessageBox.critical(self, '错误', f'获取机器码失败: {e}')

    def on_device_binding_changed(self):
        is_checked = self.device_binding_checkbox.isChecked()
        self.machine_id_input.setEnabled(is_checked)
        self.paste_btn.setEnabled(is_checked)
        
        if not is_checked:
            self.machine_id_input.setPlaceholderText('未启用绑定，无需输入')
        else:
            self.machine_id_input.setPlaceholderText('请粘贴用户提供的机器码')
            if not self.machine_id_input.text():
                # 尝试自动获取一次填入（提升体验）
                try:
                    code = LicenseValidator.get_machine_fingerprint()
                    if "ERROR" not in code:
                        self.machine_id_input.setText(code)
                except:
                    pass
                self.machine_id_input.setFocus()

    def generate_license(self):
        try:
            require_binding = self.device_binding_checkbox.isChecked()
            machine_id = self.machine_id_input.text().strip()
            
            if not require_binding:
                machine_id = "ANY_DEVICE"

            days = self.days_spinbox.value()
            hours = self.hours_spinbox.value()
            minutes = self.minutes_spinbox.value()

            if require_binding and len(machine_id) < 2:
                QMessageBox.warning(self, '⚠️ 提示', '请输入有效的机器码')
                return
            
            total_minutes = days * 24 * 60 + hours * 60 + minutes
            max_minutes = 7 * 24 * 60
            if total_minutes > max_minutes:
                 QMessageBox.warning(self, '⚠️ 提示', '有效期不能超过 7 天')
                 self.days_spinbox.setValue(7)
                 self.hours_spinbox.setValue(0)
                 self.minutes_spinbox.setValue(0)
                 return
            
            if total_minutes == 0:
                QMessageBox.warning(self, '⚠️ 提示', '有效期不能为 0')
                return

            self.generate_btn.setEnabled(False)
            self.info_label.setText('⏳ 生成中...')
            QApplication.processEvents()

            license_key = generate_license(
                device_fingerprint=machine_id,
                days_valid=days,
                hours_valid=hours,
                minutes_valid=minutes,
                require_device_binding=require_binding
            )

            if not license_key:
                raise Exception("生成结果为空")

            self.current_license = license_key

            now = datetime.datetime.now()
            expiration = (now + datetime.timedelta(minutes=total_minutes)).strftime("%Y-%m-%d %H:%M")
            binding_str = "是" if require_binding else "否"
            period_str = f"{days}天"
            if hours > 0: period_str += f"{hours}小时"
            if minutes > 0: period_str += f"{minutes}分"

            display_text = (
                f"=== License 生成成功 ===\n"
                f"机器码: {machine_id}\n"
                f"有效期: {period_str}\n"
                f"过期时间: {expiration}\n"
                f"强制绑定: {binding_str}\n"
                f"------------------------\n"
                f"KEY (复制下方内容):\n"
                f"{license_key}\n"
            )
            
            self.result_text.setText(display_text)

            self.copy_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            self.generate_btn.setEnabled(True)
            self.info_label.setText('✅ 生成完毕')

        except Exception as e:
            self.generate_btn.setEnabled(True)
            self.info_label.setText('❌ 失败')
            QMessageBox.critical(self, '错误', str(e))

    def copy_key_to_clipboard(self):
        if self.current_license:
            QApplication.clipboard().setText(self.current_license)
            self.info_label.setText("📋 Key 已复制")

    def save_to_file(self):
        if not self.current_license:
            return

        machine_tag = self.machine_id_input.text().strip() or "unbound"
        machine_tag = "".join([c for c in machine_tag if c.isalnum() or c in ('-','_')])
        default_name = f"license_{machine_tag}.txt"
        
        file_path, _ = QFileDialog.getSaveFileName(self, "保存文件", default_name, "Text Files (*.txt)")

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.result_text.toPlainText())
                
                QMessageBox.information(self, '成功', f'文件已保存')
            except Exception as e:
                QMessageBox.critical(self, '失败', str(e))

    def reset_form(self):
        self.machine_id_input.clear()
        self.device_binding_checkbox.setChecked(False)
        self._set_period(1, 0, 0)
        self.result_text.clear()
        self.current_license = ""
        self.copy_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.info_label.setText('已重置')

def main():
    app = QApplication(sys.argv)
    window = LicenseGeneratorGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()