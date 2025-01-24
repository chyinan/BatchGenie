import os
import sys
import logging
import time
# 在程序开始时添加这些代码来禁用 absl 的警告
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 禁用 TensorFlow 日志
logging.getLogger('absl').setLevel(logging.ERROR)  # 设置 absl 日志级别

from modules.ai_controller import interpret_and_execute
from modules.prefix_handler import add_prefix
from modules.converter import batch_convert
from modules.audio_classifier import classify_audio_files
from modules.file_monitor import SmartFolderMonitor
from modules.suffix_handler import add_suffix  # 更新导入


MESSAGES = {
    'zh': {
        'select_language': '\n请选择你的语言 / Please select your language:',
        'language_options': '1. 中文\n2. English',
        'welcome': '\n欢迎使用 BatchGenie!',
        'menu_title': '请选择操作：',
        'menu_prefix': '1. 批量添加前缀',
        'menu_suffix': '2. 批量添加后缀',
        'menu_convert': '3. 批量格式转换',
        'menu_ai': '4. 使用 AI 模型解析自然语言命令',
        'menu_audio': '5. 按采样率分类音频文件',
        'menu_monitor': '6. 文件夹监控',
        'menu_exit': '7. 退出',
        'input_choice': '输入选项编号：',
        'input_folder': '请输入文件夹路径：',
        'input_files': '请输入文件路径（支持通配符，多个路径用英文逗号分隔）：',
        'input_prefix': '请输入要添加的前缀：',
        'input_suffix_folder': '请输入需要批量添加后缀的文件夹：',  # 更新提示
        'input_suffix_pattern': '请输入需要批量添加后缀的文件扩展名（如 txt）：',  # 更新提示
        'input_suffix': '请输入要添加的后缀：',  # 确保提示正确
        'input_command': '请输入你的操作指令（自然语言）：',
        'input_source_roots': '请输入源文件夹路径（多个路径用英文逗号分隔）：',
        'input_target_root': '请输入目标文件夹路径：',
        'input_file_types': '请输入要监控的文件类型（如 .wav，多个类型用英文逗号分隔）：',
        'goodbye': '感谢使用 BatchGenie, 再见!',
        'invalid_option': '无效选项，请重试！',
        'operation_complete': '操作完成！',
        'press_enter': '\n按回车键继续...',
        'input_prefix_folder': '请输入需要批量添加前缀的文件夹：',
        'input_prefix_pattern': '请输入需要批量添加前缀的文件格式（如wav）：',
    },
    'en': {
        'select_language': '\nPlease select language / 请选择语言:',
        'language_options': '1. 中文\n2. English',
        'welcome': '\nWelcome to BatchGenie!',
        'menu_title': 'Please select an operation:',
        'menu_prefix': '1. Batch Add Prefix',
        'menu_suffix': '2. Batch Add Suffix',
        'menu_convert': '3. Batch Format Convert',
        'menu_ai': '4. Use AI Model for Natural Language Commands',
        'menu_audio': '5. Classify Audio Files by Sample Rate',
        'menu_monitor': '6. Folder Monitor',
        'menu_exit': '7. Exit',
        'input_choice': 'Enter option number: ',
        'input_folder': 'Enter folder path: ',
        'input_files': 'Enter file paths (supports wildcards, separate multiple paths with commas): ',
        'input_prefix': 'Enter the prefix to add: ',
        'input_suffix_folder': 'Enter the folder path for batch suffix addition: ',  # 更新提示
        'input_suffix_pattern': 'Enter the file extension (e.g., txt): ',  # 更新提示
        'input_suffix': 'Enter the suffix to add: ',  # 确保提示正确
        'input_command': 'Enter your command (in natural language): ',
        'input_source_roots': 'Enter source folder paths (separate multiple paths with commas): ',
        'input_target_root': 'Enter target folder path: ',
        'input_file_types': 'Enter file types to monitor (e.g., .wav, separate with commas): ',
        'goodbye': 'Thanks for using BatchGenie, goodbye!',
        'invalid_option': 'Invalid option, please try again!',
        'operation_complete': 'Operation complete!',
        'press_enter': '\nPress Enter to continue...',
        'input_prefix_folder': 'Enter the folder path for batch prefix addition: ',
        'input_prefix_pattern': 'Enter the file pattern (e.g., *.wav): ',
    }
}

def select_language():
    while True:
        print(MESSAGES['zh']['select_language'])
        print(MESSAGES['zh']['language_options'])
        choice = input('1/2: ').strip()
        if choice == '1':
            return 'zh'
        elif choice == '2':
            return 'en'

def handle_prefix(msg, lang):
    """处理批量添加前缀操作"""
    folder_path = input(msg['input_prefix_folder'])  # 输入文件夹路径
    file_extension = input(msg['input_prefix_pattern']).strip()  # 输入文件扩展名
    prefix = input(msg['input_prefix'])  # 输入前缀
    if add_prefix(folder_path, file_extension, prefix, lang):
        print(msg['operation_complete'])

def handle_suffix(msg, lang):
    """处理批量添加后缀操作"""
    folder_path = input(msg['input_suffix_folder'])  # 输入文件夹路径
    file_extension = input(msg['input_suffix_pattern']).strip()  # 输入文件扩展名
    suffix = input(msg['input_suffix'])  # 输入后缀
    if add_suffix(folder_path, file_extension, suffix, lang):
        print(msg['operation_complete'])

def handle_monitor(msg, lang):
    """处理文件夹监控操作"""
    source_roots = input(msg['input_source_roots']).split(',')
    source_roots = [s.strip() for s in source_roots]
    target_root = input(msg['input_target_root']).strip()
    file_types = input(msg['input_file_types']).split(',')
    file_types = [f.strip() for f in file_types]
    
    monitors = []
    for source_root in source_roots:
        monitor = SmartFolderMonitor(source_root, target_root, file_types, lang)
        monitors.append(monitor)
    
    try:
        for monitor in monitors:
            monitor.start()
        print(msg['monitoring_active'])
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for monitor in monitors:
            monitor.stop()
        print(msg['monitoring_stopped'])

def main(lang='zh'):
    msg = MESSAGES[lang]
    while True:
        print(f"\n{msg['welcome']}")
        print(msg['menu_title'])
        print(msg['menu_prefix'])  # 批量添加前缀
        print(msg['menu_suffix'])  # 批量添加后缀
        print(msg['menu_convert'])  # 批量格式转换
        print(msg['menu_ai'])  # 使用 AI 模型解析自然语言命令
        print(msg['menu_audio'])  # 按采样率分类音频文件
        print(msg['menu_monitor'])  # 文件夹监控
        print(msg['menu_exit'])  # 退出
        
        try:
            choice = int(input(msg['input_choice']))
            
            if choice == 1:  # 批量添加前缀
                handle_prefix(msg, lang)
            elif choice == 2:  # 批量添加后缀
                handle_suffix(msg, lang)  # 调用处理后缀的函数
            elif choice == 3:  # 批量格式转换
                folder_path = input(msg['input_folder'])
                batch_convert(folder_path, lang)
            elif choice == 4:  # AI 命令
                command = input(msg['input_command'])
                interpret_and_execute(command, lang)
            elif choice == 5:  # 音频分类
                folder_path = input(msg['input_folder'])
                classify_audio_files(folder_path, lang)
            elif choice == 6:  # 监控
                handle_monitor(msg, lang)
            elif choice == 7:  # 退出
                print(msg['goodbye'])
                break
            else:
                print(msg['invalid_option'])
            
            if choice != 6:  # 监控模式不需要按回车继续
                input(msg['press_enter'])
                
        except ValueError:
            print(msg['invalid_option'])
            input(msg['press_enter'])
        except KeyboardInterrupt:
            print("\n" + msg['goodbye'])
            break

if __name__ == "__main__":
    lang = select_language()
    main(lang)
