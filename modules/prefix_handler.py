import os
import glob

MESSAGES = {
    'zh': {
        'no_files': "没有找到匹配的文件",
        'affected_files': "以下文件将被添加前缀：",
        'rename_preview': "  {} -> {}",
        'confirm_rename': "\n是否确认添加前缀？(y/n): ",
        'rename_cancelled': "操作已取消",
        'renaming': "正在处理: {} -> {}",
        'rename_complete': "前缀添加完成",
        'rename_error': "处理文件时出错: {}"
    },
    'en': {
        'no_files': "No matching files found",
        'affected_files': "The following files will be prefixed:",
        'rename_preview': "  {} -> {}",
        'confirm_rename': "\nConfirm adding prefix? (y/n): ",
        'rename_cancelled': "Operation cancelled",
        'renaming': "Processing: {} -> {}",
        'rename_complete': "Prefix addition complete",
        'rename_error': "Error processing file: {}"
    }
}

def add_prefix(folder_path, file_extension, prefix, lang='zh'):
    """批量为文件添加前缀
    
    Args:
        folder_path (str): 文件夹路径
        file_extension (str): 文件扩展名（如 txt）
        prefix (str): 要添加的前缀
        lang (str): 语言选项
    
    Returns:
        bool: 操作是否成功
    """
    msg = MESSAGES[lang]
    try:
        # 规范化路径
        folder_path = os.path.normpath(folder_path)
        
        # 构建完整的搜索模式
        search_pattern = os.path.join(folder_path, f"*.{file_extension}")
        
        # 获取所有匹配的文件
        files = glob.glob(search_pattern)
        
        if not files:
            print(msg['no_files'])
            return False
            
        # 显示将要处理的文件
        print(msg['affected_files'])
        for file_path in files:
            new_name = prefix + os.path.basename(file_path)
            new_path = os.path.join(os.path.dirname(file_path), new_name)
            print(msg['rename_preview'].format(file_path, new_path))
        
        # 请求确认
        response = input(msg['confirm_rename']).lower()
        if response != 'y':
            print(msg['rename_cancelled'])
            return False
        
        # 执行重命名
        for file_path in files:
            try:
                new_name = prefix + os.path.basename(file_path)
                new_path = os.path.join(os.path.dirname(file_path), new_name)
                print(msg['renaming'].format(file_path, new_path))
                os.rename(file_path, new_path)
            except Exception as e:
                print(msg['rename_error'].format(str(e)))
                continue
        
        print(msg['rename_complete'])
        return True
        
    except Exception as e:
        print(msg['rename_error'].format(str(e)))
        return False 