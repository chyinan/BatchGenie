import os
import shutil
import time
import psutil  # 用于检查文件占用

MESSAGES = {
    'zh': {
        'source_not_exist': "错误：源文件/文件夹 '{}' 不存在",
        'target_exists': "错误：目标路径 '{}' 已存在",
        'moved': "已移动: {} -> {}",
        'copied': "已复制: {} -> {}",
        'move_complete': "批量移动完成！",
        'copy_complete': "批量复制完成！",
        'error': "操作过程中出错：{}",
        'file_in_use': "文件正在被其他程序使用：{}",
        'waiting': "等待文件释放: {}"
    },
    'en': {
        'source_not_exist': "Error: Source file/folder '{}' does not exist",
        'target_exists': "Error: Target path '{}' already exists",
        'moved': "Moved: {} -> {}",
        'copied': "Copied: {} -> {}",
        'move_complete': "Batch move completed!",
        'copy_complete': "Batch copy completed!",
        'error': "Error during operation: {}",
        'file_in_use': "File is in use by another program: {}",
        'waiting': "Waiting for file to be released: {}"
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

def is_file_in_use(file_path):
    """检查文件是否被占用"""
    try:
        # 尝试以独占模式打开文件
        with open(file_path, 'rb') as f:
            try:
                # 在 Windows 上尝试获取文件锁
                msvcrt = __import__('msvcrt')
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            except ImportError:
                # 在其他系统上使用 fcntl
                import fcntl
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        return False
    except (IOError, OSError):
        return True

def batch_transfer(files, target_dir, operation='move', lang='zh', wait_time=3):
    """批量移动或复制文件到指定目录"""
    try:
        # 确保目标目录存在
        os.makedirs(target_dir, exist_ok=True)
        msg = MESSAGES[lang]
        
        results = []
        for file_path in files:
            if not os.path.exists(file_path):
                print(msg['source_not_exist'].format(file_path))
                continue
            
            # 等待指定时间
            print(msg['waiting'].format(file_path))
            time.sleep(wait_time)
            
            # 检查文件是否被占用
            if is_file_in_use(file_path):
                print(msg['file_in_use'].format(file_path))
                continue
            
            # 构建目标文件路径
            filename = os.path.basename(file_path)
            target_path = os.path.join(target_dir, filename)
            
            # 获取唯一的目标路径
            target_path = _get_unique_path(target_path)
            
            # 执行操作
            if operation == 'move':
                shutil.move(file_path, target_path)
                print(msg['moved'].format(file_path, target_path))
            else:  # copy
                shutil.copy2(file_path, target_path)
                print(msg['copied'].format(file_path, target_path))
                
            results.append((file_path, target_path))
            
        # 显示完成消息
        if operation == 'move':
            print(msg['move_complete'])
        else:
            print(msg['copy_complete'])
            
        return results
        
    except Exception as e:
        print(msg['error'].format(str(e)))
        raise

def batch_move(files, target_dir, lang='zh'):
    """批量移动文件到指定目录（向后兼容）"""
    return batch_transfer(files, target_dir, 'move', lang)

def batch_copy(files, target_dir, lang='zh'):
    """批量复制文件到指定目录"""
    return batch_transfer(files, target_dir, 'copy', lang) 