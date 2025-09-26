#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
视频下载核心模块
基于 yt-dlp 的YouTube视频下载功能
"""

import os
import sys
import tempfile
import yt_dlp
from typing import Callable, Optional, Dict, Any
import logging

# 配置日志
logger = logging.getLogger(__name__)

class DownloadError(Exception):
    """下载错误异常类"""
    pass

class VideoDownloader:
    """视频下载器类"""
    
    def __init__(self, download_dir: Optional[str] = None):
        """
        初始化下载器
        
        Args:
            download_dir: 下载目录，如果为None则使用临时目录
        """
        if download_dir is None:
            # 使用项目根目录下的tmp文件夹
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.download_dir = os.path.join(current_dir, 'tmp')
        else:
            self.download_dir = download_dir
        
        # 确保下载目录存在
        os.makedirs(self.download_dir, exist_ok=True)
        logger.info(f"下载目录: {self.download_dir}")
    
    def get_ydl_options(self, on_progress: Optional[Callable[[int], None]] = None) -> Dict[str, Any]:
        """
        获取yt-dlp配置选项
        
        Args:
            on_progress: 进度回调函数
            
        Returns:
            yt-dlp配置字典
        """
        # 输出模板：标题 [视频ID].扩展名
        out_tmpl = os.path.join(self.download_dir, f'%(title)s [%(id)s].%(ext)s')
        
        def progress_hook(d):
            """进度钩子函数"""
            if d['status'] == 'downloading':
                # 计算下载百分比
                if d.get('total_bytes'):
                    percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                elif d.get('total_bytes_estimate'):
                    percent = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
                else:
                    percent = d.get('percent', 0)
                
                if on_progress:
                    on_progress(int(percent))
                    
            elif d['status'] == 'finished':
                if on_progress:
                    on_progress(100)
                logger.info(f"下载完成: {d['filename']}")
        
        ydl_opts = {
            'outtmpl': out_tmpl,
            'format': 'best[ext=mp4]/best[ext=webm]/best',  # 优先mp4，其次webm，最后最佳格式
            'merge_output_format': 'mp4',  # 合并为mp4格式
            'progress_hooks': [progress_hook] if on_progress else [],
            'quiet': False,  # 显示基本信息
            'no_warnings': False,  # 显示警告
            'ignoreerrors': False,  # 不忽略错误
            'logtostderr': False,  # 不日志到stderr
            'writethumbnail': False,  # 不下载缩略图
            'writesubtitles': False,  # 不下载字幕
            'writeautomaticsub': False,  # 不下载自动生成字幕
            'cookiefile': None,  # Cookie文件路径（如果需要）
            'http_headers': {  # 请求头
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
        
        return ydl_opts
    
    def get_video_info(self, video_url: str) -> Dict[str, Any]:
        """
        获取视频信息（不下载）
        
        Args:
            video_url: 视频URL或ID
            
        Returns:
            视频信息字典
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,  # 不下载
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                return self._format_video_info(info)
        except Exception as e:
            logger.error(f"获取视频信息失败: {e}")
            raise DownloadError(f"获取视频信息失败: {e}")
    
    def download_video(
        self, 
        video_url: str, 
        on_progress: Optional[Callable[[int], None]] = None
    ) -> Dict[str, Any]:
        """
        下载视频
        
        Args:
            video_url: 视频URL或ID
            on_progress: 进度回调函数
            
        Returns:
            下载结果信息
        """
        # 确保URL格式正确
        if not video_url.startswith(('http://', 'https://')):
            video_url = f'https://www.youtube.com/watch?v={video_url}'
        
        ydl_opts = self.get_ydl_options(on_progress)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 先获取信息（用于记录）
                info = ydl.extract_info(video_url, download=False)
                logger.info(f"开始下载: {info.get('title', '未知标题')}")
                
                # 执行下载
                ydl.download([video_url])
                
                # 获取最终文件路径
                final_filename = ydl.prepare_filename(info)
                
                result = {
                    'status': 'completed',
                    'localPath': final_filename,
                    'videoId': info.get('id', ''),
                    'title': info.get('title', ''),
                    'duration': info.get('duration', 0),
                    'filesize': os.path.getsize(final_filename) if os.path.exists(final_filename) else 0
                }
                
                logger.info(f"下载成功: {result['title']} -> {result['localPath']}")
                return result
                
        except yt_dlp.DownloadError as e:
            logger.error(f"下载错误: {e}")
            raise DownloadError(f"下载失败: {e}")
        except Exception as e:
            logger.error(f"未知错误: {e}")
            raise DownloadError(f"下载过程出错: {e}")
    
    def _format_video_info(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """格式化视频信息"""
        return {
            'id': info.get('id', ''),
            'title': info.get('title', ''),
            'description': info.get('description', '')[:200] + '...' if info.get('description') else '',
            'duration': info.get('duration', 0),
            'uploader': info.get('uploader', ''),
            'upload_date': info.get('upload_date', ''),
            'view_count': info.get('view_count', 0),
            'like_count': info.get('like_count', 0),
            'thumbnail': info.get('thumbnail', ''),
            'webpage_url': info.get('webpage_url', ''),
            'categories': info.get('categories', []),
            'tags': info.get('tags', [])[:10],  # 只取前10个标签
            'formats': [
                {
                    'format_id': fmt.get('format_id'),
                    'ext': fmt.get('ext'),
                    'filesize': fmt.get('filesize'),
                    'quality': fmt.get('quality')
                }
                for fmt in info.get('formats', [])[:5]  # 只显示前5个格式
            ]
        }

# 全局下载器实例
_default_downloader = None

def get_downloader(download_dir: Optional[str] = None) -> VideoDownloader:
    """获取下载器实例（单例模式）"""
    global _default_downloader
    if _default_downloader is None:
        _default_downloader = VideoDownloader(download_dir)
    return _default_downloader

def download_video(
    video_id: str, 
    on_progress: Optional[Callable[[int], None]] = None,
    download_dir: Optional[str] = None
) -> str:
    """
    下载视频（简化接口）
    
    Args:
        video_id: 视频ID
        on_progress: 进度回调函数
        download_dir: 下载目录
        
    Returns:
        本地文件路径
    """
    downloader = get_downloader(download_dir)
    result = downloader.download_video(video_id, on_progress)
    return result['localPath']

def get_video_info(video_url: str) -> Dict[str, Any]:
    """
    获取视频信息（简化接口）
    
    Args:
        video_url: 视频URL或ID
        
    Returns:
        视频信息字典
    """
    downloader = get_downloader()
    return downloader.get_video_info(video_url)

# 测试函数
def test_download():
    """测试下载功能"""
    import sys
    
    def progress_callback(percent: int):
        print(f"下载进度: {percent}%")
    
    try:
        # 测试获取视频信息
        print("获取视频信息...")
        info = get_video_info("dQw4w9WgXcQ")  # 使用一个已知的YouTube视频ID
        print(f"视频标题: {info['title']}")
        print(f"时长: {info['duration']}秒")
        
        # 测试下载（注释掉以避免实际下载）
        # local_path = download_video("dQw4w9WgXcQ", progress_callback)
        # print(f"下载完成: {local_path}")
        
    except Exception as e:
        print(f"测试失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(test_download())