import os
import shutil

MESSAGES = {
    'zh': {
        'source_not_exist': "错误：源文件/文件夹 '{}' 不存在",
        'target_exists': "错误：目标路径 '{}' 已存在",
        'moved': "已移动: {} -> {}",
        'copied': "已复制: {} -> {}",
        'move_complete': "批量移动完成！",
        'copy_complete': "批量复制完成！",
        'error': "操作过程中出错：{}"
    },
    'en': {
        'source_not_exist': "Error: Source file/folder '{}' does not exist",
        'target_exists': "Error: Target path '{}' already exists",
        'moved': "Moved: {} -> {}",
        'copied': "Copied: {} -> {}",
        'move_complete': "Batch move completed!",
        'copy_complete': "Batch copy completed!",
        'error': "Error during operation: {}"
    }
}

def _get_unique_path(target_path):
    """获取唯一的目标路径，通过添加数字后缀避免冲突"""
    if not os.path.exists(target_path):
        return target_path
        
    base, ext = os.path.splitext(target_path)
    counter = 1
    while os.path.exists(target_path):
        target_path = f"{base}_{counter}{ext}"
        counter += 1
    return target_path

def batch_transfer(files, target_dir, operation='move', lang='zh'):
    """批量移动或复制文件到指定目录
    
    Args:
        files (list): 要处理的文件路径列表
        target_dir (str): 目标目录路径
        operation (str): 操作类型，'move' 或 'copy'
        lang (str): 语言选项 ('zh' 或 'en')
        
    Returns:
        list: 包含(源路径, 目标路径)元组的列表
    """
    try:
        # 确保目标目录存在
        os.makedirs(target_dir, exist_ok=True)
        
        results = []
        for file_path in files:
            if not os.path.exists(file_path):
                print(MESSAGES[lang]['source_not_exist'].format(file_path))
                continue
                
            # 构建目标文件路径
            filename = os.path.basename(file_path)
            target_path = os.path.join(target_dir, filename)
            
            # 获取唯一的目标路径
            target_path = _get_unique_path(target_path)
            
            # 执行操作
            if operation == 'move':
                shutil.move(file_path, target_path)
                print(MESSAGES[lang]['moved'].format(file_path, target_path))
            else:  # copy
                shutil.copy2(file_path, target_path)  # copy2 保留元数据
                print(MESSAGES[lang]['copied'].format(file_path, target_path))
                
            results.append((file_path, target_path))
            
        # 显示完成消息
        if operation == 'move':
            print(MESSAGES[lang]['move_complete'])
        else:
            print(MESSAGES[lang]['copy_complete'])
            
        return results
        
    except Exception as e:
        print(MESSAGES[lang]['error'].format(str(e)))
        raise

def batch_move(files, target_dir, lang='zh'):
    """批量移动文件到指定目录（向后兼容）"""
    return batch_transfer(files, target_dir, 'move', lang)

def batch_copy(files, target_dir, lang='zh'):
    """批量复制文件到指定目录"""
    return batch_transfer(files, target_dir, 'copy', lang) 