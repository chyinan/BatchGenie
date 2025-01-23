import os
import shutil
import soundfile as sf
from pathlib import Path
from mutagen.mp4 import MP4
from mutagen.dsf import DSF
import warnings

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

def classify_audio_by_samplerate(folder_path):
    """
    根据音频文件的采样率将文件分类到相应的子文件夹
    
    Args:
        folder_path (str): 包含音频文件的文件夹路径
    """
    # 支持的音频文件扩展名
    AUDIO_EXTENSIONS = {'.wav', '.flac', '.aif', '.aiff', '.m4a', '.dsf', '.dff'}
    
    # 确保文件夹路径存在
    folder_path = Path(folder_path)
    if not folder_path.exists():
        raise FileNotFoundError(f"文件夹 {folder_path} 不存在")
    
    # 用于存储不同采样率的文件
    samplerate_files = {}
    
    # 遍历文件夹中的所有文件
    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in AUDIO_EXTENSIONS:
            try:
                # 根据文件格式选择不同的读取方法
                suffix = file_path.suffix.lower()
                if suffix == '.m4a':
                    samplerate = get_m4a_samplerate(file_path)
                    if samplerate is None:
                        continue
                    folder_name = f"{samplerate/1000:.1f}kHz".replace(".0", "") if samplerate >= 1000 else f"{samplerate}Hz"
                elif suffix in {'.dsf', '.dff'}:
                    folder_name = get_dsd_info(file_path)
                    if folder_name is None:
                        continue
                else:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        info = sf.info(file_path)
                        samplerate = int(info.samplerate)
                        folder_name = f"{samplerate/1000:.1f}kHz".replace(".0", "") if samplerate >= 1000 else f"{samplerate}Hz"
                
                # 将文件添加到对应采样率的列表中
                if folder_name not in samplerate_files:
                    samplerate_files[folder_name] = []
                samplerate_files[folder_name].append(file_path)
                
            except Exception as e:
                print(f"无法读取文件 {file_path.name}: {str(e)}")
    
    # 创建子文件夹并移动文件
    for samplerate, files in samplerate_files.items():
        # 创建子文件夹
        subdir = folder_path / samplerate
        subdir.mkdir(exist_ok=True)
        
        # 移动文件
        for file_path in files:
            try:
                shutil.move(str(file_path), str(subdir / file_path.name))
                print(f"已移动 {file_path.name} 到 {samplerate} 文件夹")
            except Exception as e:
                print(f"移动文件 {file_path.name} 时出错: {str(e)}")
    
    # 打印分类统计
    print("\n分类统计:")
    for samplerate, files in samplerate_files.items():
        print(f"{samplerate}: {len(files)} 个文件") 