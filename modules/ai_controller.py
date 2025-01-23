# ai_controller.py
import os
import json
import time
import shutil
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential
import google.generativeai as genai
from modules.renamer import batch_rename
from modules.converter import batch_convert
from config import GEMINI_API_KEY

# 配置 Gemini
genai.configure(api_key=GEMINI_API_KEY)

# 获取模型
model = genai.GenerativeModel('gemini-pro')

MESSAGES = {
    'zh': {
        'connecting': "正在连接 AI 服务...",
        'connection_failed': "AI 服务连接失败: {}",
        'check_suggestions': "建议检查：",
        'check_network': "1. 网络连接是否正常",
        'check_proxy': "2. 是否使用了代理服务器",
        'check_api_key': "3. API key 是否正确",
        'network_error': "网络连接错误，正在重试...",
        'ai_result': "AI 解析结果：",
        'affected_files': "\n受影响的文件：",
        'no_files_affected': "没有文件会受到影响",
        'confirm_execute': "\n是否执行以上操作？(y/n): ",
        'operation_cancelled': "操作已取消",
        'operation_completed': "操作已完成",
        'operation_failed': "操作失败: {}",
        'invalid_operation': "无效的操作类型: {}",
        'processing_error': "处理过程出错：{}"
    },
    'en': {
        'connecting': "Connecting to AI service...",
        'connection_failed': "AI service connection failed: {}",
        'check_suggestions': "Please check:",
        'check_network': "1. Network connection",
        'check_proxy': "2. Proxy server settings",
        'check_api_key': "3. API key validity",
        'network_error': "Network connection error, retrying...",
        'ai_result': "AI analysis result:",
        'affected_files': "\nAffected files:",
        'no_files_affected': "No files will be affected",
        'confirm_execute': "\nDo you want to proceed with these operations? (y/n): ",
        'operation_cancelled': "Operation cancelled",
        'operation_completed': "Operation completed",
        'operation_failed': "Operation failed: {}",
        'invalid_operation': "Invalid operation type: {}",
        'processing_error': "Processing error: {}"
    }
}

class FileOperation:
    def __init__(self, operation_type, source_path, target_path=None, parameters=None):
        self.type = operation_type  # rename, move, delete, copy, create_dir, create_file 等
        self.source_path = Path(source_path)
        self.target_path = Path(target_path) if target_path else None
        self.parameters = parameters or {}

    def preview(self):
        """返回此操作将影响的文件列表"""
        affected_files = []
        try:
            if self.type == "rename":
                affected_files.append(f"{self.source_path} -> {self.target_path}")
            elif self.type == "move":
                affected_files.append(f"移动: {self.source_path} -> {self.target_path}")
            elif self.type == "copy":
                affected_files.append(f"复制: {self.source_path} -> {self.target_path}")
            elif self.type == "delete":
                affected_files.append(f"删除: {self.source_path}")
            elif self.type == "create_dir":
                affected_files.append(f"创建目录: {self.source_path}")
            elif self.type == "create_file":
                affected_files.append(f"创建文件: {self.source_path}")
                if self.parameters.get('content'):
                    affected_files.append(f"文件内容: {self.parameters['content'][:100]}...")
        except Exception as e:
            affected_files.append(f"预览错误: {str(e)}")
        return affected_files

    def execute(self):
        """执行文件操作"""
        try:
            if self.type == "rename":
                self.source_path.rename(self.target_path)
            elif self.type == "move":
                shutil.move(str(self.source_path), str(self.target_path))
            elif self.type == "copy":
                shutil.copy2(str(self.source_path), str(self.target_path))
            elif self.type == "delete":
                if self.source_path.is_file():
                    self.source_path.unlink()
                else:
                    shutil.rmtree(str(self.source_path))
            elif self.type == "create_dir":
                self.source_path.mkdir(parents=True, exist_ok=True)
            elif self.type == "create_file":
                # 确保父目录存在
                self.source_path.parent.mkdir(parents=True, exist_ok=True)
                # 创建文件并写入内容
                mode = 'w' if isinstance(self.parameters.get('content', ''), str) else 'wb'
                with open(self.source_path, mode, encoding='utf-8' if mode == 'w' else None) as f:
                    if self.parameters.get('content'):
                        f.write(self.parameters['content'])
                    else:
                        f.write('')  # 创建空文件
            return True
        except Exception as e:
            print(f"执行错误: {str(e)}")
            return False

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
def get_ai_response(prompt, lang='zh'):
    """获取 AI 响应，带重试机制"""
    try:
        system_prompt = f"""你是一个文件管理助手。请分析用户的需求并返回结构化的 JSON 响应。
需要返回具体的文件操作步骤，每个步骤包含操作类型和相关参数。请确保返回的 JSON 格式完整且正确。

支持的操作类型：
- rename: 重命名文件（需要 source_path 和 target_path）
- move: 移动文件（需要 source_path 和 target_path）
- copy: 复制文件（需要 source_path 和 target_path）
- delete: 删除文件（需要 source_path）
- create_dir: 创建目录（需要 source_path）
- create_file: 创建文件（需要 source_path 和可选的 content 参数）

响应格式示例：
{{
    "description": "操作说明",
    "operations": [
        {{
            "type": "create_file",
            "source_path": "完整的文件路径，如 C:/Users/username/Desktop/test.txt",
            "parameters": {{
                "content": "文件内容"
            }}
        }}
    ]
}}

注意：
1. 所有路径必须是完整的绝对路径
2. Windows 系统中路径分隔符可以用 / 或 \\
3. 创建文件时必须指定文件扩展名

用户的请求是: {prompt}"""

        response = model.generate_content(system_prompt)
        return response.text
    except Exception as e:
        print(MESSAGES[lang]['network_error'])
        raise

def interpret_and_execute(prompt, lang='zh'):
    """解析并执行自然语言命令"""
    msg = MESSAGES[lang]
    try:
        print(msg['connecting'])
        
        # 获取 AI 响应
        response = get_ai_response(prompt, lang)
        
        try:
            # 解析 AI 响应
            result = json.loads(response)
            print(f"{msg['ai_result']}\n{result['description']}")
            
            # 创建操作列表
            operations = []
            for op in result['operations']:
                # 确保必要的字段存在
                if 'type' not in op or 'source_path' not in op:
                    print(f"无效的操作配置: {op}")
                    continue
                    
                operations.append(FileOperation(
                    operation_type=op['type'],
                    source_path=op['source_path'],
                    target_path=op.get('target_path'),  # 可选字段
                    parameters=op.get('parameters', {})
                ))
            
            # 预览将要执行的操作
            print(msg['affected_files'])
            affected_files = []
            for op in operations:
                affected_files.extend(op.preview())
            
            if not affected_files:
                print(msg['no_files_affected'])
                return
                
            for file in affected_files:
                print(f"- {file}")
            
            # 请求用户确认
            if input(msg['confirm_execute']).lower() != 'y':
                print(msg['operation_cancelled'])
                return
            
            # 执行操作
            for op in operations:
                if not op.execute():
                    print(msg['operation_failed'].format(op.type))
                    return
            
            print(msg['operation_completed'])
            
        except json.JSONDecodeError as e:
            print(f"AI 响应解析失败: {str(e)}")
            print(f"原始响应: {response}")
        except Exception as e:
            print(msg['operation_failed'].format(str(e)))
            
    except Exception as e:
        print(msg['processing_error'].format(str(e)))
