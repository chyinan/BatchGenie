import os
import glob
from pathlib import Path

MESSAGES = {
    'zh': {
        'no_files': "没有找到匹配的文件",
        'confirm_delete': "以下文件将被删除：\n{}",
        'confirm_prompt': "\n确认删除这些文件吗？(y/n): ",
        'delete_cancelled': "删除操作已取消",
        'deleting': "正在删除: {}",
        'delete_complete': "删除完成，共删除 {} 个文件",
        'delete_error': "删除文件时出错: {}"
    },
    'en': {
        'no_files': "No matching files found",
        'confirm_delete': "The following files will be deleted:\n{}",
        'confirm_prompt': "\nConfirm deletion of these files? (y/n): ",
        'delete_cancelled': "Delete operation cancelled",
        'deleting': "Deleting: {}",
        'delete_complete': "Deletion complete, {} files deleted",
        'delete_error': "Error deleting file: {}"
    }
}

def batch_delete(file_patterns, lang='zh', confirm=True):
    """批量删除文件
    
    Args:
        file_patterns (list): 文件匹配模式列表
        lang (str): 语言选项
        confirm (bool): 是否需要确认
    
    Returns:
        bool: 操作是否成功
    """
    msg = MESSAGES[lang]
    try:
        # 收集所有匹配的文件
        files_to_delete = []
        for pattern in file_patterns:
            # 规范化路径
            pattern = os.path.normpath(pattern)
            # 展开通配符
            files_to_delete.extend(glob.glob(pattern, recursive=True))
        
        if not files_to_delete:
            print(msg['no_files'])
            return False
            
        # 显示将要删除的文件
        print(msg['confirm_delete'].format('\n'.join(f"- {f}" for f in files_to_delete)))
        
        # 如果需要确认
        if confirm:
            response = input(msg['confirm_prompt']).lower()
            if response != 'y':
                print(msg['delete_cancelled'])
                return False
        
        # 执行删除
        deleted_count = 0
        for file_path in files_to_delete:
            try:
                print(msg['deleting'].format(file_path))
                os.remove(file_path)
                deleted_count += 1
            except Exception as e:
                print(msg['delete_error'].format(str(e)))
        
        print(msg['delete_complete'].format(deleted_count))
        return True
        
    except Exception as e:
        print(msg['delete_error'].format(str(e)))
        return False 