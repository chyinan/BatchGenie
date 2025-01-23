import sys
from modules.ai_controller import interpret_and_execute
from modules.renamer import batch_rename
from modules.converter import batch_convert

# 语言配置
MESSAGES = {
    'zh': {
        'select_language': '\n请选择你的语言 / Please select your language:',
        'language_options': '1. 中文\n2. English',
        'welcome': '\n欢迎使用 BatchGenie!',
        'menu_title': '请选择操作：',
        'menu_rename': '1. 批量重命名',
        'menu_convert': '2. 批量格式转换',
        'menu_ai': '3. 使用 AI 模型解析自然语言命令',
        'menu_exit': '4. 退出',
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
        'menu_convert': '2. Batch Format Conversion',
        'menu_ai': '3. Use AI Model to Process Natural Language Commands',
        'menu_exit': '4. Exit',
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
    
    while True:
        print(msg['welcome'])
        print(msg['menu_title'])
        print(msg['menu_rename'])
        print(msg['menu_convert'])
        print(msg['menu_ai'])
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
            print(msg['goodbye'])
            sys.exit(0)
        else:
            print(msg['invalid_option'])

if __name__ == "__main__":
    main()
