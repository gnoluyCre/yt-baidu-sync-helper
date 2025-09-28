import argparse
import sys
from typing import Callable

import yt_dlp

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


import os
import json
from core.baidupan import handle_upload


# 百度网盘配置（可以从环境变量或配置文件中读取）
BAIDU_ACCESS_TOKEN = os.getenv('BAIDU_ACCESS_TOKEN', '121.27a0fc94de7788692e21f2132e18c48f.YGb5RHek4rGuPuCoMhL8nsZgBWZIUNtjaIbPXBY.0oT7xQ')


def handle_upload_command(video_id: str, local_path: str):
    """处理上传命令"""
    print(f"开始上传视频 {video_id}: {local_path}")

    # 检查文件是否存在
    if not os.path.exists(local_path):
        send_json({
            'status': 'error',
            'message': f'文件不存在: {local_path}',
            'videoId': video_id
        })
        return

    # 执行上传
    result = handle_upload(video_id, local_path, BAIDU_ACCESS_TOKEN)
    send_json(result)

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
    # 获取项目根目录下的tmp文件夹
    project_root = os.path.dirname(os.path.abspath(__file__))  # 项目根目录
    tmp_dir = os.path.join(project_root, 'tmp')

    # 如果tmp目录不存在，则创建它
    os.makedirs(tmp_dir, exist_ok=True)

    out_tmpl = os.path.join(tmp_dir, f'%(title)s [{video_id}].%(ext)s')

    def progress_hook(d):
        if d['status'] == 'downloading':
            pct = d.get('downloaded_bytes', 0) / (d.get('total_bytes') or 1) * 100
            on_progress(int(pct))
        elif d['status'] == 'finished':
            on_progress(100)

    ydl_opts = {
        'outtmpl': out_tmpl,
        'format': 'bestvideo+bestaudio/best',
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
        # raw = '{"cmd":"upload","videoId":"1k5hLBdQU5E","localPath":"C:/Users/IGR/Desktop/yt-baidu-sync/yt-baidu-sync-helper/tmp/BTC仍下跌！一路向下不回頭？反彈是否有可能？ [1k5hLBdQU5E].mp4"}'
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
                elif req.get('cmd') == 'upload':
                    print("指令识别为：upload")
                    localPath = req['localPath']
                    access_token = BAIDU_ACCESS_TOKEN
                    videoId =req['videoId']
                    resp = handle_upload(videoId, localPath, access_token)
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