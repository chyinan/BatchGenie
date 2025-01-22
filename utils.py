import os

def check_folder_exists(folder_path):
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹 {folder_path} 不存在！")

def validate_path(path):
    """验证路径是否存在且可访问"""
    if not path:
        return False
    return os.path.exists(path) and os.access(path, os.R_OK | os.W_OK)

def get_supported_formats():
    """从配置文件获取支持的文件格式"""
    from config import SUPPORTED_FORMATS
    return SUPPORTED_FORMATS

def sanitize_filename(filename):
    """清理文件名，移除非法字符"""
    import re
    # 移除非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    return filename.strip()
