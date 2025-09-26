"""
百度网盘同步助手核心模块
"""

# 版本信息
__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "YouTube视频下载与百度网盘同步工具"

# 导入下载模块功能
from .download import (
    VideoDownloader,
    download_video,
    get_video_info,
    DownloadError,
    get_downloader
)

# 导入百度网盘模块功能
from .baidupan import (
    BaiduPanUploader,
    handle_upload
)

# 定义公开的API接口
__all__ = [
    # 下载相关
    'VideoDownloader',
    'download_video',
    'get_video_info',
    'DownloadError',
    'get_downloader',

    # 百度网盘相关
    'BaiduPanUploader',
    'handle_upload',
]

# 包初始化代码
def init_package():
    """包初始化函数"""
    import os
    import logging

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 创建必要的临时目录
    current_dir = os.path.dirname(os.path.dirname(__file__))
    temp_dir = os.path.join(current_dir, 'tmp')
    os.makedirs(temp_dir, exist_ok=True)

    print(f"核心模块初始化完成，临时目录: {temp_dir}")

# 自动初始化
init_package()