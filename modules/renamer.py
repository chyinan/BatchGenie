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

def batch_rename(files, prefix=''):
    """批量重命名文件，添加指定前缀"""
    try:
        results = []
        for file_path in files:
            if not os.path.exists(file_path):
                continue
                
            # 获取文件目录和文件名
            directory = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            
            # 构建新文件名（添加前缀）
            new_filename = f"{prefix}{filename}"
            new_filepath = os.path.join(directory, new_filename)
            
            # 重命名文件
            os.rename(file_path, new_filepath)
            results.append((file_path, new_filepath))
            
        return results
    except Exception as e:
        print(f"重命名操作失败: {str(e)}")
        raise
