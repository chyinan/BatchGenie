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

def batch_rename(files, new_names):
    """批量重命名文件"""
    try:
        results = []
        for file_path, new_name in zip(files, new_names):
            if not os.path.exists(file_path):
                continue
                
            # 获取文件目录
            directory = os.path.dirname(file_path)
            
            # 构建新文件路径
            new_filepath = os.path.join(directory, new_name)
            
            # 重命名文件
            os.rename(file_path, new_filepath)
            results.append((file_path, new_filepath))
            
        return results
    except Exception as e:
        print(f"重命名操作失败: {str(e)}")
        raise
