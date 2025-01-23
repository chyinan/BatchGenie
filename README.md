# BatchGenie（批量精灵）- 智能文件管理助手 🪄✨

[English](#english) | [中文](#中文)

# 中文

BatchGenie 是一款基于 AI 的用户友好型工具，旨在简化和优化批量文件操作。无论是重命名文件、格式转换，还是执行自定义指令，BatchGenie 让您可以通过自然语言轻松管理文件。无论您是技术达人还是初学者，它都能让文件管理变得更加轻松！

## 功能特性

- 🖋 **批量重命名：** 快速为多个文件添加前缀。
- 🔄 **批量格式重命名：** 轻松实现多文件格式之间的重命名。
- 🤖 **AI 驱动指令：** 使用自然语言描述文件操作，让 BatchGenie 为您完成工作。
- 🎵 **音频文件分类：** 自动识别并分类不同采样率的音频文件。
  - 支持常见音频格式（WAV, FLAC, AIF, AIFF, M4A）
  - 支持 DSD 格式（DSF, DFF），自动识别 DSD64/128/256/512
  - 自动创建采样率子文件夹并分类整理
- 🛠 **模块化设计：** 基于 Python，功能可轻松扩展和定制。

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

4. 音频文件分类
   - 自动识别音频文件采样率
   - 创建对应采样率的子文件夹（如 44.1kHz、48kHz、96kHz、DSD128 等）
   - 自动将音频文件移动到对应文件夹

## 注意事项

- 使用前建议备份重要文件
- AI 功能需要有效的 OpenAI API key
- 确保有足够的磁盘权限

---

# English

# BatchGenie - Your Intelligent File Management Assistant 🪄✨

BatchGenie is an AI-powered, user-friendly tool designed to streamline and simplify batch file operations. Whether you're renaming files, converting formats, or executing custom commands, BatchGenie enables you to interact with your files effortlessly using natural language instructions. Perfect for both tech-savvy users and beginners alike!

## Key Features:
- 🖋 **Batch Rename:** Quickly add prefixes.
- 🔄 **Batch Format Rename:** Convert multiple files between different formats with ease.
- 🤖 **AI-Powered Commands:** Use natural language to describe file operations and let BatchGenie do the rest.
- 🎵 **Audio File Classification:** Automatically identify and classify audio files by sample rate.
  - Supports common audio formats (WAV, FLAC, AIF, AIFF, M4A)
  - Supports DSD formats (DSF, DFF) with automatic DSD64/128/256/512 detection
  - Creates sample rate subfolders and organizes files automatically
- 🛠 **Customizable:** Easily extend functionality with modular and scalable Python code.

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

4. Audio Classification
   - Automatically detect audio file sample rates
   - Create corresponding subfolders (e.g., 44.1kHz, 48kHz, 96kHz, DSD128)
   - Move audio files to appropriate folders

## Notes

- Backup important files before use
- AI features require a valid OpenAI API key
- Ensure sufficient disk permissions

## Requirements

- Python 3.6+
- OpenAI API key
- Required packages listed in `requirements.txt`
