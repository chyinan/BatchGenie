import os
import json
from modules.ai_controller import get_ai_response  # 确保 AI 控制器已导入

class UndoHandler:
    def __init__(self):
        self.last_operation = None

    def record_operation(self, operation_type, params):
        """记录最后一次操作"""
        self.last_operation = (operation_type, params)

    def undo_last_operation(self):
        """撤回最后一次操作"""
        if self.last_operation is None:
            print("没有操作可以撤回。")
            return

        operation_type, params = self.last_operation
        print(f"上一次操作: {operation_type}，参数: {params}")

        # 获取受影响的文件列表
        affected_files = self.get_affected_files(operation_type, params)
        if not affected_files:
            print("没有找到受影响的文件，无法执行撤回操作。")
            return

        # 向 AI 提交上一次操作的细节和受影响的文件列表
        ai_response = get_ai_response(f"撤回操作: {operation_type}，参数: {params}，受影响的文件: {affected_files}")

        # 解析 AI 返回的操作
        try:
            operation = json.loads(ai_response)
            self.execute_undo_operation(operation)
        except json.JSONDecodeError:
            print("AI 响应解析失败，请手动撤回。")
            return

        # 清空最后一次操作记录
        self.last_operation = None

    def preview_and_confirm_undo(self, operation):
        """预览撤回操作并确认是否执行"""
        operation_type = operation.get("operation")
        params = operation.get("params")

        # 获取受影响的文件列表
        affected_files = self.get_affected_files(operation_type, params)
        if not affected_files:
            print("没有找到受影响的文件，无法执行撤回操作。")
            return

        print("以下文件将受到撤回操作影响：")
        for old_path, new_path in affected_files:
            print(f"  {new_path} -> {old_path}")

        # 用户确认
        confirm = input("是否确认撤回操作？(y/n): ")
        if confirm.lower() == "y":
            self.execute_undo_operation(operation)
        else:
            print("撤回操作已取消。")

    def get_affected_files(self, operation_type, params):
        """获取受影响的文件列表"""
        folder_path = os.path.normpath(params[0])  # 确保路径格式正确
        file_extension = params[1]
        affected_files = []

        if operation_type == "add_prefix":
            prefix = params[2]
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(f".{file_extension}"):
                    new_name = f"{prefix}{filename}"
                    affected_files.append(
                        (os.path.join(folder_path, filename), os.path.join(folder_path, new_name))
                    )

        elif operation_type == "remove_suffix":
            suffix = params[2]
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(f"{suffix}.{file_extension}"):
                    old_name = filename[:-len(suffix)] + f".{file_extension}"
                    affected_files.append(
                        (os.path.join(folder_path, old_name), os.path.join(folder_path, filename))
                    )

        elif operation_type == "remove_prefix":
            prefix = params[2]
            for filename in os.listdir(folder_path):
                if filename.startswith(prefix) and filename.lower().endswith(f".{file_extension}"):
                    old_name = filename[len(prefix):]
                    affected_files.append(
                        (os.path.join(folder_path, old_name), os.path.join(folder_path, filename))
                    )

        elif operation_type == "rename_format":
            new_extension = params[1]
            original_extension = params[2]  # 确保获取原始扩展名
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(new_extension):
                    base_name = os.path.splitext(filename)[0]
                    old_name = f"{base_name}{original_extension}"
                    affected_files.append(
                        (os.path.join(folder_path, old_name), os.path.join(folder_path, filename))
                    )

        return affected_files

    def execute_undo_operation(self, operation):
        """执行 AI 返回的撤回操作"""
        operation_type = operation.get('operation')
        params = operation.get('params')

        if operation_type == 'remove_prefix':
            folder_path, file_extension, prefix = params
            self._remove_prefix(folder_path, file_extension, prefix)
        elif operation_type == 'remove_suffix':
            folder_path, file_extension, suffix = params
            self._remove_suffix(folder_path, file_extension, suffix)
        elif operation_type == 'remove_rename_format':
            folder_path, new_extension, original_extension = params
            self._rename_format(folder_path, new_extension, original_extension)  # 确保传递原始扩展名
        else:
            print("未知的撤回操作。")

    def _remove_prefix(self, folder_path, file_extension, prefix):
        """执行移除前缀的操作"""
        for filename in os.listdir(folder_path):
            if filename.startswith(prefix) and filename.lower().endswith(f".{file_extension}"):
                old_name = filename[len(prefix):]
                try:
                    os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, old_name))
                    print(f"已撤回: {os.path.join(folder_path, filename)} -> {os.path.join(folder_path, old_name)}")
                except Exception as e:
                    print(f"无法撤回文件 {os.path.join(folder_path, filename)}: {e}")

    def _remove_suffix(self, folder_path, file_extension, suffix):
        """执行移除后缀的操作"""
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(f"{suffix}.{file_extension}"):
                old_name = filename[:-len(suffix)] + f".{file_extension}"
                try:
                    os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, old_name))
                    print(f"已撤回: {os.path.join(folder_path, filename)} -> {os.path.join(folder_path, old_name)}")
                except Exception as e:
                    print(f"无法撤回文件 {os.path.join(folder_path, filename)}: {e}")

    def _rename_format(self, folder_path, new_extension, original_extension):
        """执行格式重命名的操作"""
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(new_extension):
                base_name = os.path.splitext(filename)[0]
                # 确保 original_extension 以点开头
                if not original_extension.startswith('.'):
                    original_extension = '.' + original_extension
                new_name = f"{base_name}{original_extension}"  # 确保添加点
                new_path = os.path.join(folder_path, new_name)
                try:
                    os.rename(os.path.join(folder_path, filename), new_path)
                    print(f"已撤回: {os.path.join(folder_path, filename)} -> {new_path}")
                except Exception as e:
                    print(f"无法撤回文件 {os.path.join(folder_path, filename)}: {e}")
