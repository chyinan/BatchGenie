import os
import sys
import logging
import time
# 在程序开始时添加这些代码来禁用 absl 的警告
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 禁用 TensorFlow 日志
logging.getLogger('absl').setLevel(logging.ERROR)  # 设置 absl 日志级别

from modules.ai_controller import interpret_and_execute
from modules.renamer import batch_rename
from modules.converter import batch_convert
from modules.audio_classifier import classify_audio_files
from modules.file_monitor import SmartFolderMonitor  # 更新为新的监控类

# 语言配置
MESSAGES = {
    'zh': {
        'select_language': '\n请选择你的语言 / Please select your language:',
        'language_options': '1. 中文\n2. English',
        'welcome': '\n欢迎使用 BatchGenie!',
        'menu_title': '请选择操作：',
        'menu_rename': '1. 批量重命名',
        'menu_convert': '2. 批量格式重命名',
        'menu_ai': '3. 使用 AI 模型解析自然语言命令操作文件',
        'menu_audio': '4. 按采样率分类音频文件',
        'menu_exit': '5. 退出',
        'input_choice': '输入选项编号：',
        'input_folder': '请输入文件夹路径：',
        'input_prefix': '请输入新文件名前缀：',
        'input_command': '请输入你的操作指令（自然语言）：',
        'goodbye': '感谢使用 BatchGenie, 再见!',
        'invalid_option': '无效选项，请重试！'
    },
    'en': {
        'select_language': '\nPlease select language / 请选择语言:',
        'language_options': '1. 中文\n2. English',
        'welcome': '\nWelcome to BatchGenie!',
        'menu_title': 'Please select an operation:',
        'menu_rename': '1. Batch Rename',
        'menu_convert': '2. Batch Format Rename',
        'menu_ai': '3. Use AI Model to Process Natural Language Commands',
        'menu_audio': '4. Classify Audio Files by Sample Rate',
        'menu_exit': '5. Exit',
        'input_choice': 'Enter option number: ',
        'input_folder': 'Enter folder path: ',
        'input_prefix': 'Enter new filename prefix: ',
        'input_command': 'Enter your command (in natural language): ',
        'goodbye': 'Thanks for using BatchGenie, goodbye!',
        'invalid_option': 'Invalid option, please try again!'
    }
}

MENU_MESSAGES = {
    'zh': {
        'welcome': "欢迎使用 BatchGenie！",
        'select_operation': "请选择操作：",
        'options': [
            "批量重命名",
            "批量格式重命名",
            "使用 AI 模型处理自然语言命令",
            "按采样率分类音频文件",
            "退出"
        ],
        'enter_option': "请输入选项编号：",
        'enter_folder': "请输入文件夹路径：",
        'enter_command': "请输入您的命令：",
        'invalid_option': "无效的选项，请重试",
        'press_enter': "\n按回车键继续..."
    },
    'en': {
        'welcome': "Welcome to BatchGenie!",
        'select_operation': "Please select an operation:",
        'options': [
            "Batch Rename",
            "Batch Format Rename",
            "Use AI Model to Process Natural Language Commands",
            "Classify Audio Files by Sample Rate",
            "Exit"
        ],
        'enter_option': "Enter option number:",
        'enter_folder': "Enter folder path:",
        'enter_command': "Enter your command:",
        'invalid_option': "Invalid option, please try again",
        'press_enter': "\nPress Enter to continue..."
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

def main(lang='zh'):
    msg = MENU_MESSAGES[lang]
    while True:
        print(f"\n{msg['welcome']}")
        print(f"{msg['select_operation']}")
        for i, option in enumerate(msg['options'], 1):
            print(f"{i}. {option}")
            
        try:
            choice = int(input(f"{msg['enter_option']} "))
            
            if choice == 3:  # AI 命令处理
                command = input(f"{msg['enter_command']} ")
                interpret_and_execute(command, lang)
                input(msg['press_enter'])  # 等待用户按回车继续
            elif choice == 4:  # 音频分类
                folder_path = input(f"{msg['enter_folder']} ")
                classify_audio_files(folder_path, lang)
                input(msg['press_enter'])  # 等待用户按回车继续
            elif choice == 5:  # 退出
                break
            # ... 其他选项的处理 ...
            
        except ValueError:
            print(msg['invalid_option'])
            input(msg['press_enter'])  # 等待用户按回车继续
        except KeyboardInterrupt:
            print("\n")
            break

if __name__ == "__main__":
    main()
