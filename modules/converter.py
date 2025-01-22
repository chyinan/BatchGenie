import os

def batch_convert(folder_path):
    """
    批量修改文件扩展名
    
    Args:
        folder_path (str): 文件夹路径
    """
    try:
        if not os.path.exists(folder_path):
            print(f"错误：文件夹 '{folder_path}' 不存在")
            return
            
        source_format = input("请输入需要修改的格式（例如: .mp4）: ").strip().lower()
        if not source_format.startswith('.'):
            source_format = '.' + source_format
            
        target_format = input("请输入目标格式（例如: .m4a）: ").strip().lower()
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
                print(f"已重命名: {filename} -> {new_filename}")
                count += 1
        
        if count > 0:
            print(f"批量重命名完成！共处理 {count} 个文件")
        else:
            print(f"未找到任何 {source_format} 格式的文件")
            
    except Exception as e:
        print(f"处理过程中出错：{str(e)}")
