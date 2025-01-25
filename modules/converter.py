import os

MESSAGES = {
    'zh': {
        'folder_not_exist': "错误：文件夹 '{}' 不存在",
        'input_source_format': "请输入需要修改的格式（例如: .mp4）: ",
        'input_target_format': "请输入目标格式（例如: .m4a）: ",
        'renamed': "已重命名: {} -> {}",
        'complete': "批量重命名完成！共处理 {} 个文件",
        'no_files': "未找到任何 {} 格式的文件",
        'error': "处理过程中出错：{}"
    },
    'en': {
        'folder_not_exist': "Error: Folder '{}' does not exist",
        'input_source_format': "Enter source format (e.g., .mp4): ",
        'input_target_format': "Enter target format (e.g., .m4a): ",
        'renamed': "Renamed: {} -> {}",
        'complete': "Batch conversion completed! Processed {} files",
        'no_files': "No files found with {} format",
        'error': "Error during processing: {}"
    }
}

def batch_convert(folder_path, original_extension, target_extension, lang='zh'):
    """批量修改文件扩展名"""
    msg = MESSAGES[lang]
    try:
        if not os.path.exists(folder_path):
            print(msg['folder_not_exist'].format(folder_path))
            return False
            
        count = 0
        files = os.listdir(folder_path)
        for filename in files:
            if filename.lower().endswith(original_extension):
                old_path = os.path.join(folder_path, filename)
                new_filename = filename[:-len(original_extension)] + target_extension
                new_path = os.path.join(folder_path, new_filename)
                os.rename(old_path, new_path)
                print(msg['renamed'].format(filename, new_filename))
                count += 1
        
        if count > 0:
            print(msg['complete'].format(count))
            return True  # 返回 True 表示成功处理文件
        else:
            print(msg['no_files'].format(original_extension))
            return False  # 返回 False 表示没有处理文件
            
    except Exception as e:
        print(msg['error'].format(str(e)))
        return False  # 返回 False 表示发生错误
