"""
mitmproxy代理服务模块
"""

import asyncio, socket, os
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster

from .addons import ResponseModifierAddon

# 全局插件实例，用于外部控制
global_addon_instance = None

async def start_proxy_async():
    """
    异步启动mitmproxy代理服务
    """
    global global_addon_instance

    def get_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', 0))
            return s.getsockname()[1]

    port = get_free_port()
    opts = Options(
        listen_host='127.0.0.1',
        listen_port=port,
    )

    def get_settings_path():
        """获取设置文件路径"""
        appdata_path = os.getenv('APPDATA')
        if not appdata_path:
            # 如果无法获取APPDATA，则使用当前目录
            appdata_path = os.path.dirname(os.path.abspath(__file__))
        settings_dir = os.path.join(appdata_path, "绿杉树")
        os.makedirs(settings_dir, exist_ok=True)
        return os.path.join(settings_dir, "port.txt")
    
    with open(get_settings_path(), 'w', encoding='utf-8') as f:
        f.write(str(port))

    # 创建DumpMaster实例
    m = DumpMaster(opts)
    
    # 创建并添加响应修改插件
    global_addon_instance = ResponseModifierAddon()
    m.addons.add(global_addon_instance)

    try:
        print(f"代理服务已启动，监听端口: {opts.listen_port}")
        await m.run()
    except Exception as e:
        print(f"代理运行出错: {e}")
    finally:
        m.shutdown()

def run_in_thread():
    """
    在子线程中运行代理服务
    """
    asyncio.run(start_proxy_async())

def get_addon_instance():
    """
    获取全局插件实例
    """
    return global_addon_instance