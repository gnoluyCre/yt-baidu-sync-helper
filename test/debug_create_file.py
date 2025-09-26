#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
专门调试创建文件步骤 - 修复版
"""

import json
import sys
import os
import logging

logging.basicConfig(level=logging.DEBUG)
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.baidupan import BaiduPanUploader


def debug_create_file():
    access_token = "121.27a0fc94de7788692e21f2132e18c48f.YGb5RHek4rGuPuCoMhL8nsZgBWZIUNtjaIbPXBY.0oT7xQ"  # 替换为你的token
    uploader = BaiduPanUploader(access_token)

    # 测试创建目录
    # print("=== 测试创建目录 ===")
    # result = uploader.create_directory("/apps/yt-download")  # /apps/appName/mydir
    # print(f"目录创建结果: {result}")

    # 测试预创建（获取uploadid）
    print("\n=== 测试预创建 ===")
    file_path = r"C:\Users\IGR\Desktop\yt-baidu-sync\yt-baidu-sync-helper\tmp\BTC仍下跌！一路向下不回頭？反彈是否有可能？ [1k5hLBdQU5E].mp4"  # 替换为实际文件路径

    # 确保测试文件存在
    if not os.path.exists(file_path):
        print(f"测试文件不存在: {file_path}")
        # 创建一个小的测试文件
        with open(file_path, 'wb') as f:
            f.write(b'test content for baidu pan upload')
        print("已创建测试文件")

    remote_path = "/apps/yt-download/test_file.mp4"

    print("跳过预上传")
    # precreate_result = uploader.precreate_upload(file_path, remote_path)

    # print(f"预创建结果: {precreate_result}")

    # if precreate_result and precreate_result.get('errno') == 0:
    #     uploadid = precreate_result.get('uploadid')
    #     block_list = precreate_result.get('block_list', [])
    #
    #     print(f"uploadid: {uploadid}")
    #     print(f"block_list: {block_list}")
    #
    #     # 测试创建文件（不实际上传分片）
    #     print("\n=== 测试创建文件 ===")
    #     create_result = uploader.create_file(os.path.getsize(file_path), remote_path, uploadid, block_list)
    #     print(f"创建文件结果: {create_result}")
    # else:
    #     print("预创建失败，无法继续测试创建文件")

    # 直接上传



if __name__ == "__main__":
    debug_create_file()