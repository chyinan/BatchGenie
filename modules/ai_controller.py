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
import glob
from .prefix_handler import add_prefix
from .file_transfer import batch_move, batch_copy
from .file_monitor import SmartFolderMonitor  # 只导入新的监控类

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
        'ai_result': "AI 分析结果：",
        'affected_files': "受影响的文件：",
        'no_files_affected': "没有文件会受到影响",
        'confirm_execute': "是否执行以上操作？(y/n): ",
        'operation_cancelled': "操作已取消",
        'operation_completed': "操作完成",
        'operation_failed': "操作失败：{}",
        'invalid_operation': "无效的操作类型: {}",
        'processing_error': "处理出错：{}",
        'invalid_params': "无效的监控参数",
        'monitor_settings': "\n监控设置：",
        'source_roots': "源文件夹列表:\n{}",
        'target_root': "目标文件夹: {}",
        'file_types': "文件类型: {}",
        'monitoring_active': "所有监控器已启动，按 Ctrl+C 停止...",
        'monitoring_stopped': "所有监控器已停止",
        'paths_not_exist': "以下路径不存在：\n{}\n请检查路径是否正确。"
    },
    'en': {
        'connecting': "Connecting to AI service...",
        'connection_failed': "AI service connection failed: {}",
        'check_suggestions': "Please check:",
        'check_network': "1. Network connection",
        'check_proxy': "2. Proxy server settings",
        'check_api_key': "3. API key validity",
        'network_error': "Network connection error, retrying...",
        'ai_result': "AI Analysis Result:",
        'affected_files': "Affected files:",
        'no_files_affected': "No files will be affected",
        'confirm_execute': "Do you want to proceed with these operations? (y/n): ",
        'operation_cancelled': "Operation cancelled",
        'operation_completed': "Operation completed",
        'operation_failed': "Operation failed: {}",
        'invalid_operation': "Invalid operation type: {}",
        'processing_error': "Processing error: {}",
        'invalid_params': "Invalid monitor parameters",
        'monitor_settings': "\nMonitor Settings:",
        'source_roots': "Source directories:\n{}",
        'target_root': "Target directory: {}",
        'file_types': "File types: {}",
        'monitoring_active': "All monitors are active, press Ctrl+C to stop...",
        'monitoring_stopped': "All monitors have been stopped",
        'paths_not_exist': "The following paths do not exist:\n{}\nPlease check if the paths are correct."
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

        1. 添加前缀：
        {{
            "operation": "add_prefix",
            "files": [
                "C:/path/to/*.txt"
            ],
            "prefix": "PREFIX_"
        }}

        2. 移动文件：
        {{
            "operation": "move",
            "files": [
                "C:/source/path/*.txt"
            ],
            "target_dir": "C:/target/path"
        }}

        3. 智能文件夹监控：
        {{
            "operation": "smart_monitor",
            "source_roots": [
                "D:/DRV VST PROJECT/htdemucs",
                "D:/DRV VST PROJECT/htdemucs_6s",
                "D:/DRV VST PROJECT/htdemucs_ft"
            ],
            "target_root": "D:/DRV VST PROJECT/DRV-SA-InstVoc-Custom",
            "file_types": [".wav"]
        }}

        注意：
        1. 对于批量操作，请使用通配符（如 *.wav）来匹配文件
        2. 确保返回的是标准的 JSON 格式
        3. 路径中的反斜杠需要使用正斜杠替代
        4. 文件类型要包含点号（如 .wav）
        5. 多个源文件夹路径要放在 source_roots 数组中

        用户的请求是: {prompt}"""
        
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

def _normalize_path(path):
    """规范化路径字符串，处理空格和斜杠问题"""
    # 替换所有反斜杠为正斜杠
    path = path.replace('\\', '/')
    # 移除多余的正斜杠
    path = '/'.join(filter(None, path.split('/')))
    # 转换回系统路径格式
    return os.path.normpath(path)

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
            
            # 获取操作类型和参数
            operation = result.get('operation')
            
            if operation == 'smart_monitor':
                # 获取并规范化监控参数
                source_roots = [_normalize_path(src) for src in result.get('source_roots', [])]
                target_root = _normalize_path(result.get('target_root', ''))
                file_types = result.get('file_types', ['.wav'])
                
                if not source_roots or not target_root:
                    print(msg['invalid_params'])
                    return
                
                # 验证所有路径是否存在
                invalid_paths = []
                for src in source_roots:
                    if not os.path.exists(src):
                        invalid_paths.append(src)
                
                if invalid_paths:
                    print(msg['paths_not_exist'].format('\n'.join(f"- {p}" for p in invalid_paths)))
                    return
                
                # 显示监控设置
                print(msg['monitor_settings'])
                print(msg['source_roots'].format('\n'.join(f"- {src}" for src in source_roots)))
                print(msg['target_root'].format(target_root))
                print(msg['file_types'].format(', '.join(file_types)))
                
                # 创建多个监控器
                monitors = []
                for source_root in source_roots:
                    monitor = SmartFolderMonitor(
                        source_root,
                        target_root,
                        file_types,
                        lang
                    )
                    monitors.append(monitor)
                
                # 启动所有监控器
                for monitor in monitors:
                    monitor.start()
                
                print(msg['monitoring_active'])
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    for monitor in monitors:
                        monitor.stop()
                    print(msg['monitoring_stopped'])
            
            elif operation == 'add_prefix':
                if not add_prefix(result.get('files', []), result.get('prefix', '')):
                    print(msg['operation_failed'].format(operation))
                    return
            elif operation == 'move':
                if not batch_move(result.get('files', []), result.get('target_dir'), lang):
                    print(msg['operation_failed'].format(operation))
                    return
            elif operation == 'copy':
                if not batch_copy(result.get('files', []), result.get('target_dir'), lang):
                    print(msg['operation_failed'].format(operation))
                    return
            else:
                print(msg['invalid_operation'].format(operation))
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
        
        if operation == 'add_prefix':
            prefix = response_json.get('prefix', '')
            if files and prefix:
                return add_prefix(files, prefix)
        elif operation == 'rename':
            new_names = response_json.get('new_names', [])
            if files and new_names and len(files) == len(new_names):
                return batch_rename(files, new_names)
        
        print("无效的操作参数")
        return None
            
    except Exception as e:
        print(f"处理指令失败: {str(e)}")
        return None
