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
import glob  # 添加这个导入

# 配置 Gemini
genai.configure(api_key=GEMINI_API_KEY)

# 获取模型
model = genai.GenerativeModel('gemini-pro')

# 获取当前用户的主目录
USER_HOME = Path.home()
DOCUMENTS_PATH = USER_HOME / "Documents"
MUSIC_PATH = USER_HOME / "Music"
PICTURES_PATH = USER_HOME / "Pictures"
DESKTOP_PATH = USER_HOME / "Desktop"

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

def replace_placeholders(prompt):
    """替换用户目录的占位符为实际路径"""
    prompt = prompt.replace("桌面", str(DESKTOP_PATH))
    prompt = prompt.replace("文档", str(DOCUMENTS_PATH))
    prompt = prompt.replace("音乐", str(MUSIC_PATH))
    prompt = prompt.replace("图片", str(PICTURES_PATH))
    return prompt

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
def get_ai_response(prompt, lang='zh'):
    """获取 AI 响应，带重试机制"""
    try:
        # 替换用户目录的占位符
        prompt = replace_placeholders(prompt)

        # 检查输入是否有效
        if not prompt or prompt.strip() == "":
            raise ValueError("输入的提示不能为空。")

        print(f"输入的提示: '{prompt}'")  # 调试输出

        system_prompt = f"""你是一个文件管理助手。请分析用户的需求并返回结构化的 JSON 响应。
        以下是返回格式的示例：
        {{
            "operation": "add_prefix",
            "files": [
                "C:/path/to/*.txt"
            ],
            "prefix": "PREFIX_",
            "description": "为指定文件添加前缀"
        }}
        
        注意：
        1. 对于批量操作，请使用通配符（如 *.txt）来匹配文件
        2. 返回的 JSON 中不要包含任何注释
        3. 确保返回的是标准的 JSON 格式
        
        用户的请求是: {prompt}
        请确保返回的内容是有效的 JSON 格式，不要包含任何 Markdown 代码块标记或注释。"""
        
        response = model.generate_content(system_prompt)
        response_text = response.text
        
        # 清理响应文本，移除可能的 Markdown 代码块标记
        if response_text.startswith('```'):
            response_text = response_text.split('\n', 1)[1]
        if response_text.endswith('```'):
            response_text = response_text.rsplit('\n', 1)[0]
        if response_text.startswith('json'):
            response_text = response_text.split('\n', 1)[1]
            
        # 移除任何行内注释
        response_lines = response_text.split('\n')
        cleaned_lines = []
        for line in response_lines:
            comment_index = line.find('#')
            if comment_index != -1:
                line = line[:comment_index].rstrip()
            cleaned_lines.append(line)
        response_text = '\n'.join(cleaned_lines)
            
        print(f"原始响应: {response_text}")  # 调试输出
        return response_text
            
    except Exception as e:
        print(MESSAGES[lang]['network_error'])
        print(f"详细错误信息: {str(e)}")  # 输出详细错误信息
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
            
            # 获取操作类型和参数
            operation = result.get('operation')
            file_patterns = result.get('files', [])
            prefix = result.get('prefix', '')
            
            # 展开通配符，获取实际的文件列表
            files = []
            for pattern in file_patterns:
                # 将路径分隔符统一为系统风格
                pattern = pattern.replace('/', os.path.sep)
                # 展开通配符
                matched_files = glob.glob(pattern)
                files.extend(matched_files)
            
            # 显示将要执行的操作
            print(msg['affected_files'])
            affected_files = []
            
            if operation == 'add_prefix' and files and prefix:
                for file_path in files:
                    new_name = os.path.join(
                        os.path.dirname(file_path),
                        f"{prefix}{os.path.basename(file_path)}"
                    )
                    affected_files.append(f"- {file_path} -> {new_name}")
            
            if not affected_files:
                print(msg['no_files_affected'])
                return
                
            for file in affected_files:
                print(file)
            
            # 请求用户确认
            if input(msg['confirm_execute']).lower() != 'y':
                print(msg['operation_cancelled'])
                return
            
            # 执行操作
            if operation == 'add_prefix':
                if not process_files(files, 'rename', prefix):
                    print(msg['operation_failed'].format(operation))
                    return
            
            print(msg['operation_completed'])
            
        except json.JSONDecodeError as e:
            print(f"AI 响应解析失败: {str(e)}")
            print(f"原始响应: {response}")
            
    except Exception as e:
        print(msg['processing_error'].format(str(e)))

def process_files(files, operation, prefix=''):
    """处理文件操作"""
    try:
        if operation == 'rename':
            # 确保前缀不为空且为字符串类型
            if not isinstance(prefix, str):
                raise ValueError("前缀必须是字符串类型")
            if not prefix:
                raise ValueError("前缀不能为空")
                
            try:
                # 直接执行重命名操作，不再请求确认
                results = batch_rename(files, prefix)
                return results
            except Exception as e:
                print(f"执行错误: {str(e)}")
                raise
        # ... 其他操作代码 ...
    except Exception as e:
        print(f"操作失败: {str(e)}")
        raise

def process_command(command, lang='zh'):
    """处理 AI 指令"""
    try:
        # 获取 AI 响应
        response = get_ai_response(command, lang)
        
        # 解析响应
        if isinstance(response, str):
            try:
                response_json = json.loads(response)
            except json.JSONDecodeError:
                print("AI 响应格式错误")
                return

        # 获取操作类型和参数
        operation = response_json.get('operation')
        files = response_json.get('files', [])
        prefix = response_json.get('prefix', '')
        
        # 检查操作类型
        if operation == 'add_prefix' and files and prefix:
            return process_files(files, 'rename', prefix)
        else:
            print("无效的操作参数")
            return None
            
    except Exception as e:
        print(f"处理指令失败: {str(e)}")
        return None
