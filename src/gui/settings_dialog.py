"""
设置对话框模块 - 账号密码设置
"""

import os
import json
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QMessageBox, QWidget, QTextEdit,
                              QScrollArea, QFrame)
from PySide6.QtCore import Qt

class SettingsDialog(QDialog):
    """账号密码设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("高级设置")
        self.setFixedSize(800, 600)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """设置UI界面"""
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 用户名输入
        username_layout = QHBoxLayout()
        username_label = QLabel("用户名:")
        username_label.setFixedWidth(80)
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("请输入用户名")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_edit)
        layout.addLayout(username_layout)
        
        # 密码输入
        password_layout = QHBoxLayout()
        password_label = QLabel("密码:")
        password_label.setFixedWidth(80)
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("请输入密码")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit)
        layout.addLayout(password_layout)
        
        # URL替换规则输入
        url_replace_label = QLabel("URL替换规则 (JSON格式):")
        layout.addWidget(url_replace_label)
        
        # 添加示例说明
        url_example_label = QLabel('''示例格式：
{
    "https://example.com/image1.jpg": "https://cdn.example.com/image1.jpg",
    "https://style.hssenglish.com/v9.0/student/images/theme-lantern/common/bg-1080.png": "https://i1.hdslb.com/bfs/article/4b4d62a69f10b55163fb3ee4da1d2ca4fa7231e8.png"
}''')
        url_example_label.setWordWrap(True)
        url_example_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(url_example_label)
        
        self.url_replace_text = QTextEdit()
        self.url_replace_text.setMinimumHeight(120)
        layout.addWidget(self.url_replace_text)
        
        # 自定义Response函数
        response_label = QLabel("自定义Response函数 (Python代码):")
        layout.addWidget(response_label)
        
        # 添加示例说明
        response_example_label = QLabel('''示例格式：
def custom_response(flow):
    """自定义响应处理函数"""
    if "example.com" in flow.request.url:
        flow.response.text = '{"status": "modified"}'
        flow.response.headers["Content-Type"] = "application/json"
''')
        response_example_label.setWordWrap(True)
        response_example_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(response_example_label)
        
        self.response_code_text = QTextEdit()
        self.response_code_text.setMinimumHeight(200)
        layout.addWidget(self.response_code_text)
        
        # 自定义Request函数
        request_label = QLabel("自定义Request函数 (Python代码):")
        layout.addWidget(request_label)
        
        # 添加示例说明
        request_example_label = QLabel('''示例格式：
def custom_request(flow):
    """自定义请求处理函数"""
    if "login.example.com" in flow.request.url:
        flow.request.headers["Authorization"] = "Bearer token123"
''')
        request_example_label.setWordWrap(True)
        request_example_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(request_example_label)
        
        self.request_code_text = QTextEdit()
        self.request_code_text.setMinimumHeight(200)
        layout.addWidget(self.request_code_text)
        
        # 添加垂直弹簧以填充剩余空间
        layout.addStretch()
        
        # 设置滚动内容
        scroll_area.setWidget(scroll_content)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(80, 30)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存")
        save_btn.setFixedSize(80, 30)
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
    def load_settings(self):
        """加载已保存的设置"""
        settings_path = self.get_settings_path()
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.username_edit.setText(settings.get('username', ''))
                    self.password_edit.setText(settings.get('password', ''))
                    
                    # 加载URL替换规则
                    url_replacements = settings.get('url_replacements', {})
                    if url_replacements:
                        self.url_replace_text.setPlainText(json.dumps(url_replacements, ensure_ascii=False, indent=2))
                    
                    # 加载自定义代码
                    custom_response_code = settings.get('custom_response_code', '')
                    if custom_response_code:
                        self.response_code_text.setPlainText(custom_response_code)
                        
                    custom_request_code = settings.get('custom_request_code', '')
                    if custom_request_code:
                        self.request_code_text.setPlainText(custom_request_code)
        except Exception as e:
            print(f"加载设置失败: {e}")
            
    def save_settings(self):
        """保存设置"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        
        # 验证URL替换规则JSON格式
        url_replacements_str = self.url_replace_text.toPlainText().strip()
        url_replacements = {}
        if url_replacements_str:
            try:
                url_replacements = json.loads(url_replacements_str)
                if not isinstance(url_replacements, dict):
                    raise ValueError("URL替换规则必须是一个字典")
            except json.JSONDecodeError as e:
                QMessageBox.critical(self, "错误", f"URL替换规则JSON格式错误: {e}")
                return
            except ValueError as e:
                QMessageBox.critical(self, "错误", f"{e}")
                return
        
        # 获取自定义代码
        custom_response_code = self.response_code_text.toPlainText().strip()
        custom_request_code = self.request_code_text.toPlainText().strip()
        
        # 验证Python代码语法
        if custom_response_code:
            try:
                compile(custom_response_code, '<string>', 'exec')
            except SyntaxError as e:
                QMessageBox.critical(self, "错误", f"Response函数代码语法错误: {e}")
                return
                
        if custom_request_code:
            try:
                compile(custom_request_code, '<string>', 'exec')
            except SyntaxError as e:
                QMessageBox.critical(self, "错误", f"Request函数代码语法错误: {e}")
                return
        
        if not username or not password:
            QMessageBox.warning(self, "警告", "请填写完整的账号信息！")
            return
            
        settings_path = self.get_settings_path()
        try:
            settings = {
                'username': username,
                'password': password,
                'url_replacements': url_replacements,
                'custom_response_code': custom_response_code,
                'custom_request_code': custom_request_code
            }
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
                
            QMessageBox.information(self, "成功", "设置已保存！")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置失败: {e}")

    def get_settings_path(self):
        """获取设置文件路径"""
        appdata_path = os.getenv('APPDATA')
        if not appdata_path:
            # 如果无法获取APPDATA，则使用当前目录
            appdata_path = os.path.dirname(os.path.abspath(__file__))
        settings_dir = os.path.join(appdata_path, "绿杉树")
        os.makedirs(settings_dir, exist_ok=True)
        return os.path.join(settings_dir, "settings.json")