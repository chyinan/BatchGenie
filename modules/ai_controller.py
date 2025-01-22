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

def extract_folder_path(command):
    """从 AI 响应中提取文件夹路径"""
    import re
    # 尝试匹配引号中或空格后的路径
    path_match = re.search(r'["\']([^"\']+)["\']|(?:文件夹|目录|路径)\s*[：:]\s*(\S+)', command)
    if path_match:
        return path_match.group(1) or path_match.group(2)
    return None

@retry(
    stop=stop_after_attempt(3),  # 最多重试3次
    wait=wait_exponential(multiplier=1, min=4, max=10),  # 指数退避重试
    reraise=True
)
def get_ai_response(messages):
    """获取 AI 响应，带重试机制"""
    try:
        return client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            timeout=30  # 设置30秒超时
        )
    except openai.APITimeoutError:
        print("API 请求超时，正在重试...")
        raise
    except openai.APIConnectionError:
        print("网络连接错误，正在重试...")
        raise

def interpret_and_execute(prompt):
    """解析并执行自然语言命令"""
    try:
        print("正在连接 AI 服务...")
        
        # 检查是否使用离线模式
        if os.getenv('OFFLINE_MODE') == 'true':
            return handle_offline_mode(prompt)
            
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

            response = get_ai_response(messages)
            
            try:
                # 新版 API 响应格式变更
                ai_command = json.loads(response.choices[0].message.content)
                print("AI 解析结果：", json.dumps(ai_command, ensure_ascii=False, indent=2))
                
                folder_path = ai_command.get('folder_path')
                if not folder_path or not os.path.exists(folder_path):
                    print(f"错误：文件夹 '{folder_path}' 不存在")
                    return
                    
                action = ai_command.get('action', '').lower()
                params = ai_command.get('parameters', {})
                
                if action == 'rename':
                    prefix = params.get('prefix', 'file')
                    batch_rename(folder_path, prefix)
                    
                elif action == 'convert':
                    from_format = params.get('from_format', '.txt')
                    to_format = params.get('to_format', '.txt')
                    batch_convert(folder_path, to_format)
                    
                else:
                    print(f"暂不支持的操作：{action}")
                    
            except json.JSONDecodeError:
                print("AI 响应格式解析失败，尝试使用备用方案...")
                # 备用方案：简单的关键词匹配
                ai_command = response.choices[0].message.content
                folder_path = extract_folder_path(ai_command)
                
                if "重命名" in ai_command:
                    prefix = "file"  # 可以进一步改进前缀提取
                    if folder_path:
                        batch_rename(folder_path, prefix)
                    else:
                        print("未能识别文件夹路径")
                else:
                    print("无法理解的命令")
                
        except Exception as e:
            if 'insufficient_quota' in str(e):
                print("AI 服务配额已用完，切换到离线模式")
                return handle_offline_mode(prompt)
            raise
            
    except Exception as e:
        print(f"AI 处理过程出错：{str(e)}")

def handle_offline_mode(prompt):
    """离线模式下的命令处理"""
    print("正在使用离线模式处理命令...")
    
    # 简单的关键词匹配
    folder_path = extract_folder_path(prompt)
    if not folder_path:
        print("请输入有效的文件夹路径")
        folder_path = input("文件夹路径: ").strip()
    
    if "重命名" in prompt:
        prefix = input("请输入新文件名前缀: ").strip()
        if folder_path and prefix:
            batch_rename(folder_path, prefix)
    elif "转换" in prompt or "格式" in prompt:
        target_format = input("请输入目标格式 (例如: .txt): ").strip()
        if folder_path:
            batch_convert(folder_path, target_format)
    else:
        print("无法理解的命令。支持的操作：")
        print("1. 批量重命名（包含\"重命名\"关键词）")
        print("2. 格式转换（包含\"转换\"或\"格式\"关键词）")
