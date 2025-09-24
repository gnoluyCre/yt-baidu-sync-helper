#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import argparse
import tempfile
import os
import yt_dlp
from typing import Callable

HEARTBEAT_SEC = 5

def log(message: str):
    """简单的日志函数"""
    with open('/tmp/native_host.log', 'a') as f:
        f.write(f"{message}\n")

def send_json(obj):
    body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
    sys.stdout.buffer.write(len(body).to_bytes(4, 'little'))
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()

def read_json():
    raw_len = sys.stdin.buffer.read(4)
    if not raw_len:
        return None
    msg_len = int.from_bytes(raw_len, 'little')
    return json.loads(sys.stdin.buffer.read(msg_len).decode('utf-8'))

def handle_ping():
    return {'status': 'pong'}

def loop_once():
    try:
        req = read_json()
        if req is None:
            return
        if req.get('cmd') == 'ping':
            send_json(handle_ping())
        elif req.get('cmd') == 'enqueue':
            handle_enqueue(req['videoId'], req.get('title', ''))
    except Exception as e:
        log(f'Error in loop_once: {e}')
        send_json({'status': 'error', 'message': str(e)})

def download(video_id: str, on_progress: Callable[[int], None]) -> str:
    tmp_dir = tempfile.gettempdir()
    out_tmpl = os.path.join(tmp_dir, f'%(title)s [{video_id}].%(ext)s')

    def progress_hook(d):
        if d['status'] == 'downloading':
            # 更精确的进度计算
            if d.get('total_bytes'):
                pct = d.get('downloaded_bytes', 0) / d['total_bytes'] * 100
            elif d.get('total_bytes_estimate'):
                pct = d.get('downloaded_bytes', 0) / d['total_bytes_estimate'] * 100
            else:
                pct = d.get('percent', 0)  # 使用yt-dlp自己的百分比
            on_progress(int(pct))

    ydl_opts = {
        'outtmpl': out_tmpl,
        'format': 'best[ext=mp4]/best',
        'progress_hooks': [progress_hook],
        'quiet': True,
        'no_warnings': True,
    }

    url = f'https://www.youtube.com/watch?v={video_id}'
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def handle_enqueue(video_id: str, title: str):
    def on_progress(pct: int):
        send_json({'percent': pct})

    try:
        local_path = download(video_id, on_progress)
        send_json({'status': 'completed', 'localPath': local_path})
    except Exception as e:
        log(f'Download error: {e}')
        send_json({'status': 'error', 'message': str(e)})

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true', help='单条模式（行测试）')
    args = parser.parse_args()

    if args.once:
        raw = sys.stdin.readline().strip()
        if raw:
            try:
                req = json.loads(raw)
                log(f'recv: {req}')
                if req.get('cmd') == 'ping':
                    resp = handle_ping()
                elif req.get('cmd') == 'enqueue':
                    # 单条模式简化处理
                    def on_progress(pct): print(f"Progress: {pct}%")
                    local_path = download(req['videoId'], on_progress)
                    resp = {'status': 'completed', 'localPath': local_path}
                else:
                    resp = {'status': 'unknown_cmd'}
                log(f'send: {resp}')
                print(json.dumps(resp, ensure_ascii=False))
            except Exception as e:
                log(f'error: {e}')
                print(json.dumps({'status': 'error', 'message': str(e)}))
    else:
        while True:
            loop_once()

if __name__ == '__main__':
    main()