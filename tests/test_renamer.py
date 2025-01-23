import os
import tempfile
from modules.renamer import batch_rename

def test_batch_rename():
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文件
        for i in range(3):
            with open(os.path.join(temp_dir, f"file{i}.txt"), 'w') as f:
                f.write("Test content")

        # 测试重命名
        batch_rename(temp_dir, "TEST")
        renamed_files = os.listdir(temp_dir)
        assert all(name.startswith("TEST_") for name in renamed_files)
        print("测试通过：文件重命名模块")
