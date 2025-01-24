import os
import shutil
import soundfile as sf
from pathlib import Path
from mutagen.mp4 import MP4
from mutagen.dsf import DSF
import warnings

MESSAGES = {
    'zh': {
        'moved': "已移动 '{}' 到 {} 文件夹",
        'stats_header': "\n分类统计:",
        'stats_format': "{}: {} 个文件",
        'error_reading': "读取文件 '{}' 时出错: {}",
        'error_creating_dir': "创建目录 '{}' 时出错: {}",
        'error_moving': "移动文件 '{}' 时出错: {}",
        'no_audio_files': "指定目录中没有找到音频文件",
        'processing': "正在处理音频文件...",
        'complete': "音频文件分类完成！"
    },
    'en': {
        'moved': "Moved '{}' to {} folder",
        'stats_header': "\nClassification Statistics:",
        'stats_format': "{}: {} files",
        'error_reading': "Error reading file '{}': {}",
        'error_creating_dir': "Error creating directory '{}': {}",
        'error_moving': "Error moving file '{}': {}",
        'no_audio_files': "No audio files found in the specified directory",
        'processing': "Processing audio files...",
        'complete': "Audio file classification completed!"
    }
}

def get_m4a_samplerate(file_path):
    """
    获取 m4a 文件的采样率
    
    Args:
        file_path (Path): m4a 文件路径
    Returns:
        int: 采样率
    """
    try:
        audio = MP4(file_path)
        return audio.info.sample_rate
    except Exception as e:
        print(f"无法读取 m4a 文件 {file_path.name}: {str(e)}")
        return None

def get_dsd_info(file_path):
    """
    获取 DSD 文件的采样率信息
    
    Args:
        file_path (Path): DSD 文件路径
    Returns:
        str: DSD格式名称 (如 'DSD64', 'DSD128' 等)
    """
    try:
        audio = DSF(file_path)
        # DSD 基准采样率是 2.8224MHz (DSD64)
        base_rate = 2822400
        sample_rate = audio.info.sample_rate
        
        # 计算 DSD 倍率
        dsd_multiple = sample_rate / base_rate
        
        # 映射到对应的 DSD 格式名称
        if dsd_multiple == 1:
            return 'DSD64'
        elif dsd_multiple == 2:
            return 'DSD128'
        elif dsd_multiple == 4:
            return 'DSD256'
        elif dsd_multiple == 8:
            return 'DSD512'
        else:
            return f'DSD{int(dsd_multiple*64)}'
    except Exception as e:
        print(f"无法读取 DSD 文件 {file_path.name}: {str(e)}")
        return None

def classify_audio_files(folder_path, lang='zh'):
    """根据采样率对音频文件进行分类
    
    Args:
        folder_path (str): 音频文件所在文件夹路径
        lang (str): 语言选项 ('zh' 或 'en')
    """
    try:
        msg = MESSAGES[lang]
        print(msg['processing'])
        
        # 统计不同采样率的文件数量
        sample_rate_count = {}
        
        # 遍历文件夹中的所有文件
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            # 跳过文件夹
            if os.path.isdir(file_path):
                continue
                
            try:
                # 读取音频文件信息
                with sf.SoundFile(file_path) as audio_file:
                    sample_rate = audio_file.samplerate
                    
                    # 创建对应采样率的文件夹
                    rate_folder = f"{sample_rate/1000:.1f}kHz"
                    rate_path = os.path.join(folder_path, rate_folder)
                    
                    try:
                        os.makedirs(rate_path, exist_ok=True)
                    except Exception as e:
                        print(msg['error_creating_dir'].format(rate_folder, str(e)))
                        continue
                    
                    # 移动文件
                    try:
                        shutil.move(file_path, os.path.join(rate_path, filename))
                        print(msg['moved'].format(filename, rate_folder))
                        
                        # 更新统计
                        sample_rate_count[rate_folder] = sample_rate_count.get(rate_folder, 0) + 1
                        
                    except Exception as e:
                        print(msg['error_moving'].format(filename, str(e)))
                        
            except Exception as e:
                print(msg['error_reading'].format(filename, str(e)))
                
        # 显示统计信息
        if sample_rate_count:
            print(msg['stats_header'])
            for rate, count in sample_rate_count.items():
                print(msg['stats_format'].format(rate, count))
            print(msg['complete'])
        else:
            print(msg['no_audio_files'])
            
    except Exception as e:
        print(f"Error: {str(e)}")

def classify_audio_by_samplerate(folder_path):
    """
    根据音频文件的采样率将文件分类到相应的子文件夹
    
    Args:
        folder_path (str): 包含音频文件的文件夹路径
    """
    # 支持的音频文件扩展名
    AUDIO_EXTENSIONS = {'.wav', '.flac', '.aif', '.aiff', '.m4a', '.dsf', '.dff'}
    
    while True:
        try:
            # 确保文件夹路径存在
            folder_path = Path(folder_path)
            if not folder_path.exists():
                print(f"错误：文件夹 '{folder_path}' 不存在")
                folder_path = input("请重新输入有效的文件夹路径（或输入 'q' 退出）：")
                if folder_path.lower() == 'q':
                    return
                continue
            
            if not folder_path.is_dir():
                print(f"错误：'{folder_path}' 不是一个文件夹")
                folder_path = input("请重新输入有效的文件夹路径（或输入 'q' 退出）：")
                if folder_path.lower() == 'q':
                    return
                continue
            
            break
        except Exception as e:
            print(f"发生错误：{str(e)}")
            folder_path = input("请重新输入有效的文件夹路径（或输入 'q' 退出）：")
            if folder_path.lower() == 'q':
                return
            continue
    
    try:
        # 用于存储不同采样率的文件
        samplerate_files = {}
        
        # 检查文件夹中是否有支持的音频文件
        audio_files = [f for f in folder_path.iterdir() 
                      if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS]
        
        if not audio_files:
            print(f"提示：在文件夹 '{folder_path}' 中没有找到支持的音频文件")
            print(f"支持的格式：{', '.join(AUDIO_EXTENSIONS)}")
            return
        
        # 遍历文件夹中的所有文件
        for file_path in audio_files:
            try:
                # 读取音频文件信息
                info = sf.info(file_path)
                samplerate = int(info.samplerate)
                
                # 将采样率格式化为标准形式
                if samplerate >= 1000:
                    folder_name = f"{samplerate/1000:.1f}kHz".replace(".0", "")
                else:
                    folder_name = f"{samplerate}Hz"
                
                # 将文件添加到对应采样率的列表中
                if folder_name not in samplerate_files:
                    samplerate_files[folder_name] = []
                samplerate_files[folder_name].append(file_path)
                
            except Exception as e:
                print(f"警告：无法读取文件 '{file_path.name}': {str(e)}")
                continue
        
        if not samplerate_files:
            print("没有找到可以处理的音频文件")
            return
        
        # 创建子文件夹并移动文件
        for samplerate, files in samplerate_files.items():
            # 创建子文件夹
            subdir = folder_path / samplerate
            subdir.mkdir(exist_ok=True)
            
            # 移动文件
            for file_path in files:
                try:
                    shutil.move(str(file_path), str(subdir / file_path.name))
                    print(f"已移动 '{file_path.name}' 到 {samplerate} 文件夹")
                except Exception as e:
                    print(f"警告：移动文件 '{file_path.name}' 时出错: {str(e)}")
        
        # 打印分类统计
        print("\n分类统计:")
        for samplerate, files in samplerate_files.items():
            print(f"{samplerate}: {len(files)} 个文件")
            
    except Exception as e:
        print(f"处理过程中发生错误：{str(e)}")
        print("操作已取消")
        return 