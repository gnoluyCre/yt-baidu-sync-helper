#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查百度API权限
"""

import requests
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def check_baidu_permission(access_token):
    """检查百度API权限"""

    base_url = "https://pan.baidu.com/rest/2.0"

    # 测试1: 获取用户信息（基本权限）
    print("=== 测试基本权限 ===")
    try:
        response = requests.get(f"{base_url}/xpan/nas", params={
            'method': 'uinfo',
            'access_token': access_token
        }, timeout=10)
        result = response.json()
        print(f"用户信息API: {result}")
    except Exception as e:
        print(f"用户信息API失败: {e}")

    # 测试2: 获取网盘容量（需要netdisk权限）
    print("\n=== 测试网盘权限 ===")
    try:
        response = requests.get(f"{base_url}/xpan/nas", params={
            'method': 'quota',
            'access_token': access_token
        }, timeout=10)
        result = response.json()
        print(f"网盘容量API: {result}")
    except Exception as e:
        print(f"网盘容量API失败: {e}")

    # 测试3: 文件列表（需要netdisk权限）
    print("\n=== 测试文件操作权限 ===")
    try:
        response = requests.get(f"{base_url}/xpan/file", params={
            'method': 'list',
            'access_token': access_token,
            'dir': '/',
            'start': 0,
            'limit': 10
        }, timeout=10)
        result = response.json()
        print(f"文件列表API: {result}")
    except Exception as e:
        print(f"文件列表API失败: {e}")


if __name__ == "__main__":
    # 你的access_token
    access_token = "121.27a0fc94de7788692e21f2132e18c48f.YGb5RHek4rGuPuCoMhL8nsZgBWZIUNtjaIbPXBY.0oT7xQ"

    print(f"检查Access Token权限: {access_token[:20]}...")
    check_baidu_permission(access_token)