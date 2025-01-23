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

def batch_convert(folder_path, lang='zh'):
    """批量修改文件扩展名"""
    msg = MESSAGES[lang]
    try:
        if not os.path.exists(folder_path):
            print(msg['folder_not_exist'].format(folder_path))
            return
            
        source_format = input(msg['input_source_format']).strip().lower()
        if not source_format.startswith('.'):
            source_format = '.' + source_format
            
        target_format = input(msg['input_target_format']).strip().lower()
        if not target_format.startswith('.'):
            target_format = '.' + target_format
        
        count = 0
        files = os.listdir(folder_path)
        for filename in files:
            if filename.lower().endswith(source_format):
                old_path = os.path.join(folder_path, filename)
                new_filename = filename[:-len(source_format)] + target_format
                new_path = os.path.join(folder_path, new_filename)
                os.rename(old_path, new_path)
                print(msg['renamed'].format(filename, new_filename))
                count += 1
        
        if count > 0:
            print(msg['complete'].format(count))
        else:
            print(msg['no_files'].format(source_format))
            
    except Exception as e:
        print(msg['error'].format(str(e)))
