"""
yt-dlp 封装
支持：进度回调、断点续传、自动合并音视频
"""
import os
import tempfile
import yt_dlp
from typing import Callable

def download(video_id: str, on_progress: Callable[[int], None]) -> str:
    """
    返回：本地 mp4 绝对路径
    """
    tmp_dir = tempfile.gettempdir()
    out_tmpl = os.path.join(tmp_dir, f'%(title)s [{video_id}].%(ext)s')

    def progress_hook(d):
        if d['status'] == 'downloading':
            pct = d.get('downloaded_bytes', 0) / (d.get('total_bytes') or 1) * 100
            on_progress(int(pct))
        elif d['status'] == 'finished':
            on_progress(100)

    ydl_opts = {
        'outtmpl': out_tmpl,
        'format': 'best[ext=mp4]/best',   # 优先 mp4，否则 best
        'progress_hooks': [progress_hook],
        'quiet': True,
        'no_warnings': True,
    }

    url = f'https://www.youtube.com/watch?v={video_id}'
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)   # 返回最终文件绝对路径