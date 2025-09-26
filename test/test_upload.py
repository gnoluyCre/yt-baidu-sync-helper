#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
上传测试脚本
"""

import json
import sys
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 设置为DEBUG级别查看详细日志
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.baidupan import handle_upload


def test_upload():
    # 测试数据
    test_data = {
        "cmd": "upload",
        "videoId": "1k5hLBdQU5E",
        "localPath": r"C:\Users\IGR\Desktop\yt-baidu-sync\yt-baidu-sync-helper\tmp\BTC仍下跌！一路向下不回頭？反彈是否有可能？ [1k5hLBdQU5E].mp4"
    }

    print("测试数据:")
    print(json.dumps(test_data, ensure_ascii=False, indent=2))

    # 检查文件是否存在
    if not os.path.exists(test_data["localPath"]):
        print(f"错误: 文件不存在 - {test_data['localPath']}")
        # 列出tmp目录内容帮助调试
        tmp_dir = os.path.dirname(test_data["localPath"])
        if os.path.exists(tmp_dir):
            print(f"tmp目录内容: {os.listdir(tmp_dir)}")
        return

    print(f"文件存在，大小: {os.path.getsize(test_data['localPath'])} 字节")

    # 设置百度访问令牌（替换为你的真实令牌）
    access_token = os.getenv('BAIDU_ACCESS_TOKEN', '121.27a0fc94de7788692e21f2132e18c48f.YGb5RHek4rGuPuCoMhL8nsZgBWZIUNtjaIbPXBY.0oT7xQ')
    if access_token == '121.27a0fc94de7788692e21f2132e18c48f.YGb5RHek4rGuPuCoMhL8nsZgBWZIUNtjaIbPXBY.0oT7xQ':
        print("警告: 使用默认访问令牌，可能需要替换为真实令牌")

    print("开始上传测试...")

    # 执行上传
    result = handle_upload(
        test_data["videoId"],
        test_data["localPath"],
        access_token
    )

    print("\n上传结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    test_upload()