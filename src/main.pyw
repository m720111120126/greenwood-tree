#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
绿杉树 - 主程序入口
"""

import sys
import os
import threading
import asyncio
import ctypes
import subprocess
import base64

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_cmd(command):
    """执行命令并返回输出和返回码"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def check_task_exists(task_name):
    """检查任务计划程序中是否存在指定名称的任务"""
    code, output, error = run_cmd(f'schtasks /Query /TN "{task_name}" /FO LIST')
    # 如果任务存在，命令会成功执行（返回码0）；如果不存在，会提示错误。
    return code == 0

def run_task(task_name):
    """立即运行指定的任务"""
    code, out, err = run_cmd(f'schtasks /Run /TN "{task_name}"')
    if code == 0:
        print(f"🚀 任务 '{task_name}' 已触发执行。")
        return True
    else:
        print(f"❌ 任务执行失败: {err}")
        return False

def create_install_task(task_name, command):
    print(f"创建任务: {task_name}, command: {command}")
    """创建一个任务"""
    # PowerShell 脚本逻辑
    # 1. 检查任务是否存在，如果存在则删除（强制更新）
    # 2. 创建一个新的任务定义，设置电源设置为“允许在电池下运行”
    ps_script = f'''$TaskName = "{task_name.replace('"', '`"')}"
$Command = "{command.replace('"', '`"')}"
    
# 如果任务已存在，先删除
if (schtasks /Query /TN $TaskName /FO LIST 2>$null) {{
    schtasks /Delete /TN $TaskName /F
}}
    
# 使用 schtasks 创建任务（基础创建）
# 这里的 trick 是：我们稍后会用 Set-ScheduledTask 来修改它的设置
$Result = schtasks /Create /TN $TaskName /TR "$Command" /SC ONCE /ST 00:00 /RL HIGHEST /F
    
# --- 关键步骤：使用 PowerShell 的 Set-ScheduledTask 修改电源设置 ---
# 获取任务对象
$Task = Get-ScheduledTask -TaskName $TaskName

$Task.Settings.StopIfGoingOnBatteries = $False
$Task.Settings.DisallowStartIfOnBatteries = $False
    
# 应用修改
Set-ScheduledTask -InputObject $Task
    
exit 0
'''
    
    try:
        encoded_script = base64.b64encode(ps_script.encode('utf-16le')).decode()
    except Exception as e:
        print(f"编码脚本失败: {e}")
        return False

    # 3. 调用 PowerShell 执行编码后的内容
    # -WindowStyle Hidden : 隐藏窗口
    # -EncodedCommand : 解码并执行
    cmd = f'powershell -WindowStyle Hidden -EncodedCommand {encoded_script}'
    
    code, out, err = run_cmd(cmd)
    print(f"任务创建输出: {out}, 错误: {err}, 返回码: {code}")
    if code == 0:
        print(f"✅ 任务 '{task_name}' 创建成功 (已配置允许电池运行)。")
        return True
    else:
        print(f"❌ 任务创建失败: {err}")
        return False

if is_admin():
    if "python" in sys.executable:
        create_install_task("绿杉树启动-python", f'"cmd.exe" /c "{sys.executable}" "{" ".join(sys.argv)}"')
    else:
        create_install_task("绿杉树启动", f'"{os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "start.vbs")}"')
else:
    if check_task_exists("绿杉树启动") or ("python" in sys.executable and check_task_exists("绿杉树启动-python")):
        run_task("绿杉树启动" if not "python" in sys.executable else "绿杉树启动-python")
        sys.exit(0)
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 0)
        sys.exit(0)

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.gui.browser_window import ModernBrowser
from src.proxy.mitmproxy_service import run_in_thread

if __name__ == "__main__":
    # 设置Windows事件循环策略
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # 启动代理服务线程（始终保持连接）
    proxy_thread = threading.Thread(target=run_in_thread, name="Mitmproxy-Worker", daemon=True)
    proxy_thread.start()
    
    # 等待代理服务启动
    import time
    time.sleep(2)  # 给代理服务启动时间
    
    # 启动GUI应用程序
    from src.gui.application import create_application
    app = create_application()
    window = ModernBrowser()
    window.show()
    sys.exit(app.exec())