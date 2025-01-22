import sys
from modules.ai_controller import interpret_and_execute
from modules.renamer import batch_rename
from modules.converter import batch_convert

def main():
    while True:
        print("\n欢迎使用 BatchGenie! ")
        print("请选择操作：")
        print("1. 批量重命名")
        print("2. 批量格式转换")
        print("3. 使用 AI 模型解析自然语言命令")
        print("4. 退出")

        choice = input("输入选项编号：")
        if choice == "1":
            folder = input("请输入文件夹路径：")
            prefix = input("请输入新文件名前缀：")
            batch_rename(folder, prefix)
        elif choice == "2":
            folder = input("请输入文件夹路径：")
            batch_convert(folder)
        elif choice == "3":
            prompt = input("请输入你的操作指令（自然语言）：")
            interpret_and_execute(prompt)
        elif choice == "4":
            print("感谢使用 BatchGenie, 再见! ")
            sys.exit(0)
        else:
            print("无效选项，请重试！")

if __name__ == "__main__":
    main()
