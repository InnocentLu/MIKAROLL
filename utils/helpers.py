"""utils/helpers.py - 文件名辅助函数"""
import os


def get_unique_filename(path: str) -> str:
    """
    若文件已存在，则自动在文件名后追加 (1), (2)... 直到找到不冲突的路径。
    例如: output.pdf -> output (1).pdf -> output (2).pdf
    """
    if not os.path.exists(path):
        return path

    base, ext = os.path.splitext(path)
    counter = 1
    while True:
        new_path = f"{base} ({counter}){ext}"
        if not os.path.exists(new_path):
            return new_path
        counter += 1
