#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Native Messaging Host 骨架
读一行 JSON → 回一行 JSON
"""
import sys
import json
import argparse

LOG_F = sys.stderr   # 调试日志输出到 stderr，不会污染 stdout

def log(msg):
    print(msg, file=LOG_F, flush=True)

def read_stdin_line():
    """Native Messaging 协议：先读 4 字节长度，再读 body"""
    raw_len = sys.stdin.buffer.read(4)
    if not raw_len:
        return None
    msg_len = int.from_bytes(raw_len, byteorder='little')
    msg = sys.stdin.buffer.read(msg_len).decode('utf-8')
    return json.loads(msg)

def write_stdout_line(obj):
    """先写 4 字节长度，再写 body"""
    body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
    sys.stdout.buffer.write(len(body).to_bytes(4, byteorder='little'))
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()

def handle_ping():
    return {'status': 'pong', 'msg': 'helper alive'}

def loop_once():
    try:
        req = read_stdin_line()
        if req is None:
            return
        log(f'recv: {req}')
        if req.get('cmd') == 'ping':
            resp = handle_ping()
        else:
            resp = {'status': 'unknown_cmd'}
        log(f'send: {resp}')
        write_stdout_line(resp)
    except Exception as e:
        log(f'error: {e}')
        write_stdout_line({'status': 'error', 'message': str(e)})

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true', help='单条模式（命令行测试）')
    args = parser.parse_args()

    if args.once:
        # 单条模式：直接读 stdin 一行 JSON（无 4 字节头）
        raw = sys.stdin.readline().strip()
        if raw:
            try:
                req = json.loads(raw)
                log(f'recv: {req}')
                if req.get('cmd') == 'ping':
                    resp = handle_ping()
                else:
                    resp = {'status': 'unknown_cmd'}
                log(f'send: {resp}')
                print(json.dumps(resp, ensure_ascii=False))
            except Exception as e:
                log(f'error: {e}')
                print(json.dumps({'status': 'error', 'message': str(e)}))
    else:
        # 正式 Native Messaging 循环
        while True:
            loop_once()

if __name__ == '__main__':
    main()