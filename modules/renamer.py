import os

MESSAGES = {
    'zh': {
        'folder_not_exist': "错误：文件夹 '{}' 不存在",
        'renamed': "已重命名: {} -> {}",
        'rename_complete': "批量重命名完成！",
        'error': "重命名过程中出错：{}"
    },
    'en': {
        'folder_not_exist': "Error: Folder '{}' does not exist",
        'renamed': "Renamed: {} -> {}",
        'rename_complete': "Batch rename completed!",
        'error': "Error during renaming: {}"
    }
}

def batch_rename(folder_path, prefix, lang='zh'):
    """
    批量重命名指定文件夹中的文件
    
    Args:
        folder_path (str): 文件夹路径
        prefix (str): 新文件名前缀
    """
    msg = MESSAGES[lang]
    try:
        if not os.path.exists(folder_path):
            print(msg['folder_not_exist'].format(folder_path))
            return
            
        files = os.listdir(folder_path)
        for filename in files:
            old_path = os.path.join(folder_path, filename)
            if os.path.isfile(old_path):
                # 保持原文件名，只在前面添加前缀
                new_filename = f"{prefix}{filename}"
                new_path = os.path.join(folder_path, new_filename)
                os.rename(old_path, new_path)
                print(msg['renamed'].format(filename, new_filename))
        
        print(msg['rename_complete'])
    except Exception as e:
        print(msg['error'].format(str(e)))
