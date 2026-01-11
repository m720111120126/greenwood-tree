"""
应用程序配置模块
"""

import sys
import os
import ctypes
from PySide6.QtWidgets import QApplication
from PySide6.QtNetwork import QNetworkProxy

def install_certificate():
    """安装mitmproxy证书"""
    cert_path = os.path.expanduser("~/.mitmproxy/mitmproxy-ca-cert.cer")
    
    # 确保证书文件存在
    while not os.path.exists(cert_path):
        print(f"证书文件未找到: {cert_path}")
        # 这里可以添加等待逻辑或错误处理
    
    # 构建certutil命令
    cmd_command = f'certutil -addstore -f ROOT "{cert_path}"'
    
    # 使用管理员权限执行命令
    result = ctypes.windll.shell32.ShellExecuteW(
        None,           # 父窗口句柄
        "runas",        # 动词：请求管理员权限
        "cmd.exe",      # 执行的程序：命令行解释器
        f'/c {cmd_command}', # 参数
        None,           # 默认工作目录
        0               # 隐藏窗口
    )
    
    return result > 32  # 返回执行结果

def create_application():
    """创建并配置QApplication实例"""
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("绿杉树")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("绿杉树开发组")
    
    # 始终设置代理连接（无论模式如何）
    proxy = QNetworkProxy()
    proxy.setType(QNetworkProxy.ProxyType.HttpProxy)
    proxy.setHostName("127.0.0.1")
    # 从文件读取端口号
    def get_settings_path():
        """获取设置文件路径"""
        appdata_path = os.getenv('APPDATA')
        if not appdata_path:
            # 如果无法获取APPDATA，则使用当前目录
            appdata_path = os.path.dirname(os.path.abspath(__file__))
        settings_dir = os.path.join(appdata_path, "绿杉树")
        os.makedirs(settings_dir, exist_ok=True)
        return os.path.join(settings_dir, "port.txt")
    settings_path = get_settings_path()
    with open(settings_path, 'r', encoding='utf-8') as f:
        port = int(f.read().strip())
    
    proxy.setPort(port)
    QNetworkProxy.setApplicationProxy(proxy)
    print("应用程序已设置为始终连接代理")
    
    # 安装证书
    if install_certificate():
        print("证书安装成功")
    else:
        print("证书安装失败")
    
    return app