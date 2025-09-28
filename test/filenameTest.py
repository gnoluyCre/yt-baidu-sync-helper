# 生成远程文件名（清理文件名中的特殊字符）
import os

from core.baidupan import logger

file_path = "C:\\Users\\IGR\\Desktop\\yt-baidu-sync\\yt-baidu-sync-helper\\tmp\\于朦胧母亲的声明系伪造｜教美国教友躲避ICE抓人的择吉时法｜周末玄学大课堂：鬼遮眼实例与科学解读｜出门给儿童叫魂的定向秘法｜或疯或死出马仙的可怜下场｜ [Esk-pbgFaBI].webm"
filename = os.path.basename(file_path)
# 替换可能引起问题的字符
safe_filename = filename.replace('?', '_').replace('*', '_').replace('"', '_')
remote_dir = "/apps/yt-download"
remote_path = f"{remote_dir}/{safe_filename}"
print(remote_path)
logger.info(f"开始上传: {filename} -> {remote_path}")