import os
import sys
import logging
# 在程序开始时添加这些代码来禁用 absl 的警告
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 禁用 TensorFlow 日志
logging.getLogger('absl').setLevel(logging.ERROR)  # 设置 absl 日志级别

from modules.ai_controller import interpret_and_execute
from modules.renamer import batch_rename
from modules.converter import batch_convert
from modules.audio_classifier import classify_audio_by_samplerate

# 语言配置
MESSAGES = {
    'zh': {
        'select_language': '\n请选择你的1语言 / Please select your language:',
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

def select_language():
    while True:
        print(MESSAGES['zh']['select_language'])
        print(MESSAGES['zh']['language_options'])
        choice = input('1/2: ').strip()
        if choice == '1':
            return 'zh'
        elif choice == '2':
            return 'en'

def main():
    # 选择语言
    lang = select_language()
    msg = MESSAGES[lang]
    
    try:
        while True:
            print(msg['welcome'])
            print(msg['menu_title'])
            print(msg['menu_rename'])
            print(msg['menu_convert'])
            print(msg['menu_ai'])
            print(msg['menu_audio'])
            print(msg['menu_exit'])

            choice = input(msg['input_choice'])
            if choice == "1":
                folder = input(msg['input_folder'])
                prefix = input(msg['input_prefix'])
                batch_rename(folder, prefix)
            elif choice == "2":
                folder = input(msg['input_folder'])
                batch_convert(folder)
            elif choice == "3":
                prompt = input(msg['input_command'])
                interpret_and_execute(prompt, lang)
            elif choice == "4":
                folder = input(msg['input_folder'])
                classify_audio_by_samplerate(folder)
            elif choice == "5":
                print(msg['goodbye'])
                # 干净地退出程序
                os._exit(0)  # 使用 os._exit() 替代 sys.exit()
            else:
                print(msg['invalid_option'])
    except KeyboardInterrupt:
        print(msg['goodbye'])
        os._exit(0)

if __name__ == "__main__":
    main()
