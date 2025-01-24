import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .file_transfer import batch_transfer
from .prefix_handler import add_prefix

MESSAGES = {
    'zh': {
        'start_monitoring': "开始监控文件夹: {}",
        'stop_monitoring': "停止监控文件夹",
        'new_file': "检测到新文件: {}",
        'new_folder': "检测到新文件夹: {}",
        'create_target': "创建目标文件夹: {}",
        'processing': "正在处理文件: {}",
        'process_complete': "文件处理完成: {}",
        'error': "处理出错: {}",
        'recursive_monitoring': "正在递归监控所有子文件夹..."
    },
    'en': {
        'start_monitoring': "Start monitoring folder: {}",
        'stop_monitoring': "Stop monitoring folder",
        'new_file': "New file detected: {}",
        'new_folder': "New folder detected: {}",
        'create_target': "Creating target folder: {}",
        'processing': "Processing file: {}",
        'process_complete': "File processing completed: {}",
        'error': "Processing error: {}",
        'recursive_monitoring': "Recursively monitoring all subfolders..."
    }
}

class SmartFileHandler(FileSystemEventHandler):
    def __init__(self, source_root, target_root, file_types=None, lang='zh'):
        """初始化智能文件处理器
        
        Args:
            source_root (str): 源文件夹根目录（如 htdemucs 模型目录）
            target_root (str): 目标文件夹根目录
            file_types (list): 要处理的文件类型列表（如 ['.wav']）
            lang (str): 语言选项
        """
        self.source_root = os.path.abspath(source_root)
        self.target_root = os.path.abspath(target_root)
        self.file_types = file_types or ['.wav']
        self.lang = lang
        self.msg = MESSAGES[lang]
        
    def _get_relative_path(self, path):
        """获取相对于源根目录的路径"""
        return os.path.relpath(path, self.source_root)
        
    def _get_target_folder(self, source_folder):
        """根据源文件夹获取对应的目标文件夹路径"""
        relative_path = self._get_relative_path(source_folder)
        return os.path.join(self.target_root, relative_path)
        
    def on_created(self, event):
        """当检测到新文件或文件夹时触发"""
        try:
            if event.is_directory:
                # 处理新文件夹
                print(self.msg['new_folder'].format(event.src_path))
                target_dir = self._get_target_folder(event.src_path)
                os.makedirs(target_dir, exist_ok=True)
                print(self.msg['create_target'].format(target_dir))
            else:
                # 处理新文件
                file_path = event.src_path
                if not any(file_path.lower().endswith(ext.lower()) for ext in self.file_types):
                    return
                    
                print(self.msg['new_file'].format(file_path))
                
                # 获取文件所在的文件夹
                source_folder = os.path.dirname(file_path)
                target_dir = self._get_target_folder(source_folder)
                
                # 确保目标文件夹存在
                os.makedirs(target_dir, exist_ok=True)
                
                # 移动文件
                print(self.msg['processing'].format(file_path))
                results = batch_transfer(
                    [file_path],
                    target_dir,
                    'move',
                    self.lang
                )
                
                if results:
                    print(self.msg['process_complete'].format(results[0][1]))
                    
        except Exception as e:
            print(self.msg['error'].format(str(e)))

class SmartFolderMonitor:
    def __init__(self, source_root, target_root, file_types=None, lang='zh'):
        """初始化智能文件夹监控器"""
        self.source_root = source_root
        self.target_root = target_root
        self.file_types = file_types
        self.lang = lang
        self.observer = None
        self.msg = MESSAGES[lang]
        
    def start(self):
        """开始监控"""
        print(self.msg['start_monitoring'].format(self.source_root))
        print(self.msg['recursive_monitoring'])
        
        event_handler = SmartFileHandler(
            self.source_root,
            self.target_root,
            self.file_types,
            self.lang
        )
        
        self.observer = Observer()
        self.observer.schedule(
            event_handler,
            self.source_root,
            recursive=True  # 递归监控所有子文件夹
        )
        self.observer.start()
        
    def stop(self):
        """停止监控"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            print(self.msg['stop_monitoring']) 