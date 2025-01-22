# BatchGenie （批量精灵）

[English](#english) | [中文](#中文)

# 中文

BatchGenie 是一个强大的文件批处理工具，支持自然语言命令操作。

## 功能特性

- 批量重命名文件（添加前缀）
- 批量修改文件扩展名
- 支持 AI 自然语言命令（基于 OpenAI API）

## 安装说明

1. 克隆仓库：
```bash
git clone https://github.com/chyinan/BatchGenie.git
cd BatchGenie
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置：
   - 复制 `config.example.py` 为 `config.py`
   - 在 `config.py` 中设置你的 OpenAI API key

## 使用方法

运行程序：
```bash
python main.py
```

### 功能选项：
1. 批量重命名
   - 为文件添加指定前缀
   - 例如：`test.txt` -> `PREFIX_test.txt`

2. 批量格式转换
   - 修改文件扩展名
   - 例如：`.mp4` -> `.m4a`

3. AI 模式
   - 使用自然语言描述你想要执行的操作
   - 例如："帮我把文件夹里的所有图片重命名为 photo_序号"

## 注意事项

- 使用前建议备份重要文件
- AI 功能需要有效的 OpenAI API key
- 确保有足够的磁盘权限

---

# English

BatchGenie is a powerful file batch processing tool that supports natural language commands.

## Features

- Batch file renaming (add prefix)
- Batch file extension modification
- AI natural language command support (powered by OpenAI API)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/chyinan/BatchGenie.git
cd BatchGenie
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configuration:
   - Copy `config.example.py` to `config.py`
   - Set your OpenAI API key in `config.py`

## Usage

Run the program:
```bash
python main.py
```

### Options:
1. Batch Rename
   - Add prefix to files
   - Example: `test.txt` -> `PREFIX_test.txt`

2. Format Conversion
   - Modify file extensions
   - Example: `.mp4` -> `.m4a`

3. AI Mode
   - Describe your operation in natural language
   - Example: "Help me rename all images in the folder to photo_number"

## Notes

- Backup important files before use
- AI features require a valid OpenAI API key
- Ensure sufficient disk permissions

## Requirements

- Python 3.6+
- OpenAI API key
- Required packages listed in `requirements.txt`
