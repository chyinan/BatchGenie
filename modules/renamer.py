import os
import glob

MESSAGES = {
    'zh': {
        'no_files': "没有找到匹配的文件",
        'affected_files': "以下文件将被重命名：",
        'rename_preview': "  {} -> {}",
        'confirm_rename': "\n是否确认重命名？(y/n): ",
        'rename_cancelled': "重命名操作已取消",
        'renaming': "正在重命名: {} -> {}",
        'rename_complete': "重命名完成",
        'rename_error': "重命名文件时出错: {}",
        'file_not_exist': "文件不存在: {}"
    },
    'en': {
        'no_files': "No matching files found",
        'affected_files': "The following files will be renamed:",
        'rename_preview': "  {} -> {}",
        'confirm_rename': "\nConfirm rename operation? (y/n): ",
        'rename_cancelled': "Rename operation cancelled",
        'renaming': "Renaming: {} -> {}",
        'rename_complete': "Rename complete",
        'rename_error': "Error renaming file: {}",
        'file_not_exist': "File does not exist: {}"
    }
}

def batch_rename(source_path, new_name, lang='zh'):
    """重命名单个文件
    
    Args:
        source_path (str): 源文件路径
        new_name (str): 新文件名（不包含路径）
        lang (str): 语言选项
    
    Returns:
        bool: 操作是否成功
    """
    msg = MESSAGES[lang]
    try:
        # 规范化路径
        source_path = os.path.normpath(source_path)
        
        # 检查源文件是否存在
        if not os.path.exists(source_path):
            print(msg['file_not_exist'].format(source_path))
            return False
        
        # 获取目标路径
        source_dir = os.path.dirname(source_path)
        target_path = os.path.join(source_dir, new_name)
        
        # 显示预览
        print(msg['affected_files'])
        print(msg['rename_preview'].format(source_path, target_path))
        
        # 请求确认
        response = input(msg['confirm_rename']).lower()
        if response != 'y':
            print(msg['rename_cancelled'])
            return False
        
        # 执行重命名
        print(msg['renaming'].format(source_path, target_path))
        os.rename(source_path, target_path)
        print(msg['rename_complete'])
        return True
        
    except Exception as e:
        print(msg['rename_error'].format(str(e)))
        return False
