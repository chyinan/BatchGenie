import os

MESSAGES = {
    'zh': {
        'folder_not_exist': "错误：文件夹 '{}' 不存在",
        'prefix_added': "已添加前缀: {} -> {}",
        'prefix_complete': "批量添加前缀完成！",
        'error': "添加前缀过程中出错：{}"
    },
    'en': {
        'folder_not_exist': "Error: Folder '{}' does not exist",
        'prefix_added': "Added prefix: {} -> {}",
        'prefix_complete': "Batch prefix addition completed!",
        'error': "Error during adding prefix: {}"
    }
}

def add_prefix(files, prefix=''):
    """为文件添加指定前缀"""
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
        print(f"添加前缀操作失败: {str(e)}")
        raise 