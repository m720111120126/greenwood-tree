"""
mitmproxy插件模块 - 响应修改器
"""

import json, time, os, requests
from mitmproxy import http, ctx

class ResponseModifierAddon:
    """
    响应修改插件 - 修改特定URL的HTTP响应
    """
    
    def __init__(self):
        self.target_urls = [
            "https://www.hssenglish.com/student/quiz/autopaper",
            "https://www.hssenglish.com/student/studyFlow/strengthenNext",
            "https://www.hssenglish.com/student/studyFlow/next"
        ]
        self.is_enabled = False  # 默认禁用响应修改
        self.url_replacements = {}  # URL替换规则
        self.custom_response_func = None  # 自定义响应函数
        self.custom_request_func = None  # 自定义请求函数
    
    def set_enabled(self, enabled: bool):
        """设置响应修改功能是否启用"""
        self.is_enabled = enabled
        if enabled:
            ctx.log.info("绿杉树模式已启用 - 响应修改功能激活")
        else:
            ctx.log.info("绿杉树模式已禁用 - 响应修改功能暂停")
    
    def get_settings_path(self):
        """获取设置文件路径"""
        appdata_path = os.getenv('APPDATA')
        if not appdata_path:
            # 如果无法获取APPDATA，则使用当前目录
            appdata_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        settings_dir = os.path.join(appdata_path, "绿杉树")
        os.makedirs(settings_dir, exist_ok=True)
        return os.path.join(settings_dir, "settings.json")
    
    def load_custom_functions(self):
        """加载自定义函数"""
        settings_path = self.get_settings_path()
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                    # 更新URL替换规则
                    self.url_replacements = settings.get('url_replacements', {})
                    
                    # 获取自定义代码
                    custom_response_code = settings.get('custom_response_code', '')
                    custom_request_code = settings.get('custom_request_code', '')
                    
                    # 编译并设置自定义响应函数
                    if custom_response_code:
                        exec_globals = {'http': http, 'ctx': ctx, 'requests': requests}
                        exec(custom_response_code, exec_globals)
                        # 假设用户定义的函数名为 custom_response
                        if 'custom_response' in exec_globals:
                            self.custom_response_func = exec_globals['custom_response']
                    
                    # 编译并设置自定义请求函数
                    if custom_request_code:
                        exec_globals = {'http': http, 'ctx': ctx}
                        exec(custom_request_code, exec_globals)
                        # 假设用户定义的函数名为 custom_request
                        if 'custom_request' in exec_globals:
                            self.custom_request_func = exec_globals['custom_request']
                            
                    return settings.get('username', ''), settings.get('password', '')
        except Exception as e:
            ctx.log.error(f"加载自定义函数失败: {e}")
        # 如果读取失败，返回空字符串
        return '', ''
    
    def get_login_credentials(self):
        """从配置文件获取登录凭据和自定义函数"""
        username, password = self.load_custom_functions()
        return username, password
    
    def response(self, flow: http.HTTPFlow) -> None:
        # 首先尝试执行自定义响应函数
        if self.custom_response_func:
            try:
                self.custom_response_func(flow)
            except Exception as e:
                ctx.log.error(f"执行自定义响应函数时出错: {str(e)}")
        
        # 检查是否有URL替换规则需要应用
        for original_url, redirect_url in self.url_replacements.items():
            if flow.request.url == original_url:
                try:
                    # 获取目标内容
                    response = requests.get(redirect_url)
                    if response.status_code == 200:
                        # 创建新的HTTP响应，直接返回目标内容
                        flow.response = http.Response.make(
                            200,
                            response.content,
                            {
                                "Content-Type": response.headers.get("Content-Type", "application/octet-stream"),
                                "Content-Length": str(len(response.content)),
                                "Access-Control-Allow-Origin": "*",
                                "Cache-Control": "public, max-age=3600",
                                "Location": redirect_url  # 添加重定向头
                            }
                        )
                        ctx.log.info(f"已将 {original_url} 替换为目标内容: {redirect_url}")
                    else:
                        ctx.log.error(f"获取目标内容失败，状态码: {response.status_code}, URL: {redirect_url}")
                except Exception as e:
                    ctx.log.error(f"替换URL时发生错误: {str(e)}, Original: {original_url}, Redirect: {redirect_url}")
                return  # 如果已经处理了URL替换，就不再继续
        
        # 然后检查是否需要处理其他目标URL
        target_urls = [
            "https://www.hssenglish.com/student/quiz/autopaper",
            "https://www.hssenglish.com/student/studyFlow/strengthenNext",
            "https://www.hssenglish.com/student/studyFlow/next"
        ]
        
        if flow.response is None or self.is_enabled is False:
            return None
        
        # 检查当前请求的URL是否匹配目标
        if flow.request.url in target_urls:
            # 解析响应的JSON数据
            try:
                response_data = flow.response.json()
                
                if flow.request.url == "https://www.hssenglish.com/student/quiz/autopaper":
                    # 定位到需要修改的路径：testPaper.questionMap
                    question_map = response_data.get("testPaper", {}).get("questionMap", {})
                    for key, target_list in question_map.items():
                        # 遍历列表中的每个字典，修改"spelling"的值为"a"
                        for item in target_list:
                            if "例句" in response_data.get("testPaper", {})["testPaperName"]:
                                item["words"] = ["a"]
                                item["example_en_US"] = "a"
                                item["example_zh_CN"] = "a"
                                item["spelling"] = "a"
                                try:
                                    for item2 in item["answers"]:
                                        if isinstance(item2, dict):
                                            item2["correct"] = True
                                        item2["meaning"] = "a"
                                        item2["spelling"] = "a"
                                except:
                                    pass
                            else:
                                if isinstance(item, dict):
                                    item["spelling"] = "a"
                                    item["meaning"] = "a"
                                    try:
                                        for item2 in item["answers"]:
                                            if isinstance(item2, dict):
                                                item2["correct"] = True
                                            item2["meaning"] = "a"
                                            item2["spelling"] = "a"
                                    except:
                                        pass
                elif flow.request.url == "https://www.hssenglish.com/student/studyFlow/next":
                    if isinstance(response_data, dict):
                        try:
                            response_data["syllable"]
                            response_data["meaning"] = "a"
                            response_data["spelling"] = "a"
                            try:
                                for item in response_data["answers"]:
                                    if isinstance(item, dict):
                                        item["correct"] = True
                                    item["meaning"] = "a"
                                    item["spelling"] = "a"
                            except:
                                pass
                            try:
                                for item in response_data["options"]:
                                    if isinstance(item, dict):
                                        item["corrent"] = "Y"
                                    item["meaning"] = "a"
                                    item["spelling"] = "a"
                            except:
                                pass
                        except:
                            response_data["words"] = ["a"]
                            response_data["example_en_US"] = "a"
                            response_data["example_zh_CN"] = "a"
                            try:
                                for item in response_data["options"]:
                                    item["corrent"] = "Y"
                                    item["spelling"] = "a"
                                    item["meaning"] = "a"
                            except:
                                pass
                elif flow.request.url == "https://www.hssenglish.com/student/studyFlow/strengthenNext":
                    if isinstance(response_data, dict):
                        try:
                            response_data["word"]["syllable"] = "a"
                            response_data["word"]["spelling"] = "a"
                            response_data["word"]["soundMark"] = "a"
                        except:
                            pass

                # 将修改后的数据重新赋值给响应体
                modified_json = json.dumps(response_data, ensure_ascii=False)
                flow.response.text = modified_json
            
                ctx.log.info("成功修改响应数据：spelling字段已替换为'a'")
            
            except Exception as e:
                ctx.log.error(f"处理响应时出错：{str(e)}")

    def request(self, flow: http.HTTPFlow) -> None:
        # 首先尝试执行自定义请求函数
        if self.custom_request_func:
            try:
                self.custom_request_func(flow)
            except Exception as e:
                ctx.log.error(f"执行自定义请求函数时出错: {str(e)}")
        
        if flow.request.url == "https://www.hssenglish.com/student/user/login":
            ctx.log.info(f"拦截到登录请求: {flow.request.url}")
            # 修改请求为POST方法
            flow.request.method = "POST"
            # 设置请求头
            flow.request.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
            flow.request.headers["Accept-Encoding"] = "gzip, deferlate, br, zstd"
            flow.request.headers["Accept-Language"] = "zh-CN,zh;q=0.9,en;q=0.8"
            flow.request.headers["Cache-Control"] = "max-age=0"
            flow.request.headers["Connection"] = "keep-alive"
            flow.request.headers["Content-Type"] = "application/x-www-form-urlencoded"
            flow.request.headers["Host"] = "www.hssenglish.com"
            flow.request.headers["Origin"] = "https://www.hssenglish.com"
            flow.request.headers["Referer"] = "https://www.hssenglish.com/"
            flow.request.headers["Sec-Fetch-Dest"] = "document"
            flow.request.headers["Sec-Fetch-Mode"] = "navigate"
            flow.request.headers["Sec-Fetch-Site"] = "same-origin"
            flow.request.headers["Sec-Fetch-User"] = "?1"
            flow.request.headers["Upgrade-Insecure-Requests"] = "1"
            flow.request.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 QuarkPC/6.1.5.666"
            flow.request.headers["sec-ch-ua"] = '"Not?A_Brand";v="99", "Chromium";v="130"'
            flow.request.headers["sec-ch-ua-mobile"] = "?0"
            flow.request.headers["sec-ch-ua-platform"] = '"Windows"'
            timestamp = str(int(time.time() * 1000))
            flow.request.headers["x-uctiming-46938875"] = timestamp
            
            # 从配置文件获取登录凭据
            username, password = self.get_login_credentials()
            
            # 如果没有获取到有效的登录凭据，使用默认值
            while not username or not password:
                time.sleep(1)
                username, password = self.get_login_credentials()
            # 设置请求内容
            payload = {
                'userId': username,
                'password': password
            }
            
            # 将payload转换为表单数据格式
            form_data = f"userId={payload['userId']}&password={payload['password']}"
            flow.request.content = form_data.encode('utf-8')
            flow.request.headers["Content-Length"] = str(len(form_data))
            
            ctx.log.info("登录请求已修改为指定格式")

    def format_response_json(self, flow: http.HTTPFlow):
        """格式化JSON响应"""
        try:
            response_data = flow.response.json()
            flow.response.text = json.dumps(response_data, ensure_ascii=False)
        except:
            pass