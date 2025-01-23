# ai_controller.py
import openai
import os
import json
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from modules.renamer import batch_rename
from modules.converter import batch_convert
from config import OPENAI_API_KEY

# 设置代理（如果需要）
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'  # 根据你的代理设置修改

# 创建 OpenAI 客户端
client = openai.OpenAI(api_key=OPENAI_API_KEY)

MESSAGES = {
    'zh': {
        'connecting': "正在连接 AI 服务...",
        'connection_failed': "AI 服务连接失败: {}",
        'check_suggestions': "建议检查：",
        'check_network': "1. 网络连接是否正常",
        'check_proxy': "2. 是否使用了代理服务器",
        'check_api_key': "3. API key 是否正确",
        'api_timeout': "API 请求超时，正在重试...",
        'network_error': "网络连接错误，正在重试...",
        'ai_result': "AI 解析结果：",
        'folder_not_exist': "错误：文件夹 '{}' 不存在",
        'unsupported_operation': "暂不支持的操作：{}",
        'parse_failed': "AI 响应格式解析失败，尝试使用备用方案...",
        'path_not_recognized': "未能识别文件夹路径",
        'command_not_understood': "无法理解的命令",
        'offline_mode': "正在使用离线模式处理命令...",
        'enter_path': "请输入有效的文件夹路径",
        'enter_prefix': "请输入新文件名前缀: ",
        'enter_format': "请输入目标格式 (例如: .txt): ",
        'quota_exceeded': "AI 服务配额已用完，切换到离线模式",
        'processing_error': "AI 处理过程出错：{}"
    },
    'en': {
        'connecting': "Connecting to AI service...",
        'connection_failed': "AI service connection failed: {}",
        'check_suggestions': "Please check:",
        'check_network': "1. Network connection",
        'check_proxy': "2. Proxy server settings",
        'check_api_key': "3. API key validity",
        'api_timeout': "API request timed out, retrying...",
        'network_error': "Network connection error, retrying...",
        'ai_result': "AI parsing result:",
        'folder_not_exist': "Error: Folder '{}' does not exist",
        'unsupported_operation': "Unsupported operation: {}",
        'parse_failed': "AI response parsing failed, switching to fallback mode...",
        'path_not_recognized': "Could not recognize folder path",
        'command_not_understood': "Command not understood",
        'offline_mode': "Processing command in offline mode...",
        'enter_path': "Please enter a valid folder path",
        'enter_prefix': "Enter new filename prefix: ",
        'enter_format': "Enter target format (e.g., .txt): ",
        'quota_exceeded': "AI service quota exceeded, switching to offline mode",
        'processing_error': "Error during AI processing: {}"
    }
}

def extract_folder_path(command):
    """从 AI 响应中提取文件夹路径"""
    import re
    # 尝试匹配引号中或空格后的路径
    path_match = re.search(r'["\']([^"\']+)["\']|(?:文件夹|目录|路径|folder|directory|path)\s*[：:]\s*(\S+)', command)
    if path_match:
        return path_match.group(1) or path_match.group(2)
    return None

@retry(
    stop=stop_after_attempt(3),  # 最多重试3次
    wait=wait_exponential(multiplier=1, min=4, max=10),  # 指数退避重试
    reraise=True
)
def get_ai_response(messages, lang='zh'):
    """获取 AI 响应，带重试机制"""
    try:
        return client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            timeout=30  # 设置30秒超时
        )
    except openai.APITimeoutError:
        print(MESSAGES[lang]['api_timeout'])
        raise
    except openai.APIConnectionError:
        print(MESSAGES[lang]['network_error'])
        raise

def interpret_and_execute(prompt, lang='zh'):
    """解析并执行自然语言命令"""
    msg = MESSAGES[lang]
    try:
        print(msg['connecting'])
        
        # 检查是否使用离线模式
        if os.getenv('OFFLINE_MODE') == 'true':
            return handle_offline_mode(prompt, lang)
            
        try:
            # 系统提示设置更详细的指令
            system_prompt = """你是一个文件管理助手。请分析用户的需求并返回结构化的 JSON 响应。
响应格式示例：
{
    "action": "rename|convert",
    "folder_path": "具体路径",
    "parameters": {
        "prefix": "新文件名前缀",
        "from_format": "原格式",
        "to_format": "目标格式"
    }
}"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]

            response = get_ai_response(messages, lang)
            
            try:
                # 新版 API 响应格式变更
                ai_command = json.loads(response.choices[0].message.content)
                print(f"{msg['ai_result']}\n{json.dumps(ai_command, ensure_ascii=False, indent=2)}")
                
                folder_path = ai_command.get('folder_path')
                if not folder_path or not os.path.exists(folder_path):
                    print(msg['folder_not_exist'].format(folder_path))
                    return
                    
                action = ai_command.get('action', '').lower()
                params = ai_command.get('parameters', {})
                
                if action == 'rename':
                    prefix = params.get('prefix', 'file')
                    batch_rename(folder_path, prefix, lang)
                    
                elif action == 'convert':
                    from_format = params.get('from_format', '.txt')
                    to_format = params.get('to_format', '.txt')
                    batch_convert(folder_path, lang)
                    
                else:
                    print(msg['unsupported_operation'].format(action))
                    
            except json.JSONDecodeError:
                print(msg['parse_failed'])
                # 备用方案：简单的关键词匹配
                ai_command = response.choices[0].message.content
                folder_path = extract_folder_path(ai_command)
                
                if "重命名" in ai_command or "rename" in ai_command.lower():
                    prefix = "file"  # 可以进一步改进前缀提取
                    if folder_path:
                        batch_rename(folder_path, prefix, lang)
                    else:
                        print(msg['path_not_recognized'])
                else:
                    print(msg['command_not_understood'])
                
        except Exception as e:
            if 'insufficient_quota' in str(e):
                print(msg['quota_exceeded'])
                return handle_offline_mode(prompt, lang)
            print(msg['connection_failed'].format(str(e)))
            print(msg['check_suggestions'])
            print(msg['check_network'])
            print(msg['check_proxy'])
            print(msg['check_api_key'])
            return
            
    except Exception as e:
        print(msg['processing_error'].format(str(e)))

def handle_offline_mode(prompt, lang='zh'):
    """离线模式下的命令处理"""
    msg = MESSAGES[lang]
    print(msg['offline_mode'])
    
    folder_path = extract_folder_path(prompt)
    if not folder_path:
        print(msg['enter_path'])
        folder_path = input(": ").strip()
    
    if "重命名" in prompt or "rename" in prompt.lower():
        prefix = input(msg['enter_prefix']).strip()
        if folder_path and prefix:
            batch_rename(folder_path, prefix, lang)
    elif any(word in prompt.lower() for word in ["转换", "格式", "convert", "format"]):
        target_format = input(msg['enter_format']).strip()
        if folder_path:
            batch_convert(folder_path, lang)
    else:
        print(msg['command_not_understood'])
