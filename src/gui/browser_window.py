"""
浏览器窗口模块 - 主界面实现
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QCheckBox, QFrame, QPushButton)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtNetwork import QNetworkProxy
from PySide6.QtCore import Qt, QUrl, QTimer
import os
import json

class ModernBrowser(QMainWindow):
    """现代化浏览器窗口类"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
        self.check_and_prompt_settings()
        
    def setup_ui(self):
        """设置用户界面"""
        # 1. 无边框窗口设置
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(1100, 750)

        # 2. 核心外壳容器
        self.shell = QFrame(self)
        self.shell.setObjectName("Shell")
        self.update_shell_style(is_proxy=False)
        
        # 壳内主布局
        self.shell_layout = QVBoxLayout(self.shell)
        self.shell_layout.setContentsMargins(0, 0, 0, 0)
        self.shell_layout.setSpacing(0)
        self.setCentralWidget(self.shell)

        # 3. 创建界面组件
        self.create_title_bar()
        self.create_browser()

        # 4. 将组件加入主壳布局
        self.shell_layout.addWidget(self.title_bar)
        self.shell_layout.addWidget(self.browser)

        self.old_pos = None
        self.showFullScreen()
    
    def create_title_bar(self):
        """创建标题栏"""
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(45)
        self.title_bar.setStyleSheet("""
            background-color: #F8F8F8; 
            border-top-left-radius: 4px; 
            border-top-right-radius: 4px;
        """)
        
        # 标题栏内部布局
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(20, 0, 20, 0)

        # 标题文字
        self.title_label = QLabel("绿杉树")
        self.title_label.setStyleSheet("color: #333; font-weight: bold; font-size: 14px;")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()

        # 模式标签
        self.mode_label = QLabel("绿杉树模式")
        self.mode_label.setStyleSheet("color: #444; font-size: 13px; margin-right: 5px;")
        title_layout.addWidget(self.mode_label)

        # 设置按钮
        self.create_settings_button(title_layout)

        # 开关控件
        self.create_toggle_switch(title_layout)

        # 关闭按钮
        self.create_close_button(title_layout)
    
    def create_settings_button(self, parent_layout):
        """创建设置按钮"""
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(35, 35)
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.setStyleSheet("""
            QPushButton { 
                background: transparent; color: #555; 
                font-size: 16px; border: none; 
                margin-right: 10px;
            }
            QPushButton:hover { background-color: #D3D3D3; border-radius: 4px; }
        """)
        parent_layout.addWidget(self.settings_btn)
    
    def create_toggle_switch(self, parent_layout):
        """创建模式切换开关"""
        self.toggle = QCheckBox()
        self.toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle.setFixedSize(25, 25)
        self.toggle.setStyleSheet("""
            QCheckBox::indicator {
                width: 18px; height: 18px;
                border: 2px solid #999;
                background-color: white;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #34C759; 
                border: 2px solid #34C759;
                image: url(none);
            }
            QCheckBox::indicator:checked:after {
                content: "✔"; color: white; font-size: 14px;
                position: absolute; left: 2px; top: -2px;
            }
        """)
        parent_layout.addWidget(self.toggle)
    
    def create_close_button(self, parent_layout):
        """创建关闭按钮"""
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(35, 35)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton { 
                background: transparent; color: #555; 
                font-size: 18px; border: none; 
                margin-left: 10px; 
            }
            QPushButton:hover { background-color: #E81123; color: white; border-radius: 4px; }
        """)
        parent_layout.addWidget(self.close_btn)
    
    def create_browser(self):
        """创建浏览器组件"""
        self.browser = QWebEngineView()
        self.browser.load(QUrl("https://www.hssenglish.com/student/user/login"))
        self.browser.setStyleSheet("border-bottom-left-radius: 4px; border-bottom-right-radius: 4px;")
    
    def setup_connections(self):
        """设置信号连接"""
        self.toggle.stateChanged.connect(self.handle_proxy_change)
        self.close_btn.clicked.connect(self.close)
        self.settings_btn.clicked.connect(self.open_settings)
    
    def update_shell_style(self, is_proxy):
        """动态更新边框样式"""
        color = "#34C759" if is_proxy else "#FF3B30"
        self.shell.setStyleSheet(f"""
            #Shell {{
                background-color: #ffffff;
                border: 8px solid {color};
                border-radius: 16px;
            }}
        """)
    
    def handle_proxy_change(self, state):
        """处理代理模式切换 - 现在只控制响应修改功能"""
        is_checked = (state == Qt.CheckState.Checked.value) or (state == Qt.CheckState.PartiallyChecked.value)
        
        # 获取代理服务中的插件实例
        from src.proxy.mitmproxy_service import get_addon_instance
        addon_instance = get_addon_instance()
        
        if is_checked:
            print("启用绿杉树模式 - 响应修改功能激活")
            if addon_instance:
                addon_instance.set_enabled(True)
            self.update_shell_style(is_proxy=True)
        else:
            print("禁用绿杉树模式 - 响应修改功能暂停")
            if addon_instance:
                addon_instance.set_enabled(False)
            self.update_shell_style(is_proxy=False)
        
        # 显示切换提示并重新加载页面
        self.browser.setHtml("""
            <body style='background:#f8f8f8; display:flex; justify-content:center; align-items:center; 
                         height:100vh; font-family:sans-serif;'>
                <h2>正在切换绿杉树模式...</h2>
            </body>
        """)

        self.url = self.browser.url()  # 保存当前URL
        
        QTimer.singleShot(1000, self.perform_reload)
    
    def perform_reload(self):
        """执行网页重新加载"""
        target_url = QUrl(self.url)
        self.browser.load(target_url)
        print("网页已重新加载")
    
    def open_settings(self):
        """打开设置对话框"""
        from .settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def check_and_prompt_settings(self):
        """检查设置并提示用户设置账号密码"""
        if not self.has_saved_settings():
            from .settings_dialog import SettingsDialog
            dialog = SettingsDialog(self)
            result = dialog.exec()
            if result != dialog.DialogCode.Accepted:
                # 如果用户取消设置，可能需要提供默认行为或者退出
                pass
    
    def has_saved_settings(self):
        """检查是否已有保存的设置"""
        settings_path = self.get_settings_path()
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    username = settings.get('username', '')
                    password = settings.get('password', '')
                    return username.strip() != '' and password.strip() != ''
        except:
            pass
        return False
    
    def get_settings_path(self):
        """获取设置文件路径"""
        appdata_path = os.getenv('APPDATA')
        if not appdata_path:
            # 如果无法获取APPDATA，则使用当前目录
            appdata_path = os.path.dirname(os.path.abspath(__file__))
        settings_dir = os.path.join(appdata_path, "绿杉树")
        os.makedirs(settings_dir, exist_ok=True)
        return os.path.join(settings_dir, "settings.json")
    
    # 窗口拖动功能
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() < 60:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None