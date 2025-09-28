'''
预创建请求测试
'''
import os.path
from pathlib import Path

from core import BaiduPanUploader
access_token = "121.27a0fc94de7788692e21f2132e18c48f.YGb5RHek4rGuPuCoMhL8nsZgBWZIUNtjaIbPXBY.0oT7xQ"
bploder = BaiduPanUploader(access_token)
filename = "于朦胧母亲的声明系伪造｜教美国教友躲避ICE抓人的择吉时法｜周末玄学大课堂：鬼遮眼实例与科学解读｜出门给儿童叫魂的定向秘法｜或疯或死出马仙的可怜下场｜ [Esk-pbgFaBI].webm"

org_path = f"C:\\Users\\IGR\\Desktop\\yt-baidu-sync\\yt-baidu-sync-helper\\tmp\\{filename}"
t_path = Path(org_path).as_posix()

if not os.path.exists(t_path):
    print("文件不存在")
else:
    print(t_path)
    bploder.precreate_upload(file_path=t_path, remote_path=f"/apps/yt-download/{filename}")
