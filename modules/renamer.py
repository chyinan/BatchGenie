import os

def batch_rename(folder_path, prefix):
    """
    批量重命名指定文件夹中的文件
    
    Args:
        folder_path (str): 文件夹路径
        prefix (str): 新文件名前缀
    """
    try:
        if not os.path.exists(folder_path):
            print(f"错误：文件夹 '{folder_path}' 不存在")
            return
            
        files = os.listdir(folder_path)
        for filename in files:
            old_path = os.path.join(folder_path, filename)
            if os.path.isfile(old_path):
                # 保持原文件名，只在前面添加前缀
                new_filename = f"{prefix}{filename}"
                new_path = os.path.join(folder_path, new_filename)
                os.rename(old_path, new_path)
                print(f"已重命名: {filename} -> {new_filename}")
        
        print("批量重命名完成！")
    except Exception as e:
        print(f"重命名过程中出错：{str(e)}")
