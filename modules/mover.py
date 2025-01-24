import os
import shutil

MESSAGES = {
    'zh': {
        'source_not_exist': "错误：源文件/文件夹 '{}' 不存在",
        'target_exists': "错误：目标路径 '{}' 已存在",
        'moved': "已移动: {} -> {}",
        'move_complete': "批量移动完成！",
        'error': "移动过程中出错：{}"
    },
    'en': {
        'source_not_exist': "Error: Source file/folder '{}' does not exist",
        'target_exists': "Error: Target path '{}' already exists",
        'moved': "Moved: {} -> {}",
        'move_complete': "Batch move completed!",
        'error': "Error during moving: {}"
    }
}

def batch_move(files, target_dir):
    """批量移动文件到指定目录
    
    Args:
        files (list): 要移动的文件路径列表
        target_dir (str): 目标目录路径
        
    Returns:
        list: 包含(源路径, 目标路径)元组的列表
    """
    try:
        # 确保目标目录存在
        os.makedirs(target_dir, exist_ok=True)
        
        results = []
        for file_path in files:
            if not os.path.exists(file_path):
                print(MESSAGES['zh']['source_not_exist'].format(file_path))
                continue
                
            # 构建目标文件路径
            filename = os.path.basename(file_path)
            target_path = os.path.join(target_dir, filename)
            
            # 检查目标路径是否已存在
            if os.path.exists(target_path):
                # 可以选择自动重命名或跳过
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(target_path):
                    new_filename = f"{base}_{counter}{ext}"
                    target_path = os.path.join(target_dir, new_filename)
                    counter += 1
            
            # 移动文件
            shutil.move(file_path, target_path)
            results.append((file_path, target_path))
            print(MESSAGES['zh']['moved'].format(file_path, target_path))
            
        print(MESSAGES['zh']['move_complete'])
        return results
        
    except Exception as e:
        print(MESSAGES['zh']['error'].format(str(e)))
        raise 