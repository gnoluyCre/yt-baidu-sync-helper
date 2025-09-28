import os
import re
from pathlib import Path


def sanitize_file_path(file_path):
    """清理文件路径中的特殊字符"""
    path = Path(file_path).as_posix()
    print(f"处理中路径：{path}")
    return path


# 使用示例
original_path = "C:\\Users\\IGR\\Desktop\\yt-baidu-sync\\yt-baidu-sync-helper\\tmp\\于朦胧母亲的声明系伪造｜教美国教友躲避ICE抓人的择吉时法｜ 定向秘法｜或疯或死出马仙的可怜下场｜ [Esk-pbgFaBI].webm"
if not os.path.exists(original_path):
    print("文件不存在")
safe_path = sanitize_file_path(original_path)
if not os.path.exists(safe_path):
    print("文件不存在")
# print(safe_path)