import os
import json
import hashlib
import requests
import time
from typing import Dict, Optional, Tuple, Any, List
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)


class BaiduPanUploader:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://pan.baidu.com/rest/2.0"
        self.chunk_size = 4 * 1024 * 1024  # 4MB分片
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def _get_file_md5(self, file_path: str) -> str:
        """计算文件MD5"""
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def _get_file_slice_md5(self, file_path: str) -> Tuple[str, str]:
        """计算文件分片MD5（前256KB）"""
        with open(file_path, 'rb') as f:
            slice_data = f.read(256 * 1024)  # 前256KB
        slice_md5 = hashlib.md5(slice_data).hexdigest()
        content_md5_slice = hashlib.md5(slice_md5.encode()).hexdigest()
        return slice_md5, content_md5_slice

    def _get_file_info(self, file_path: str) -> Dict:
        """获取文件信息（大小、MD5等）"""
        file_size = os.path.getsize(file_path)
        content_md5 = self._get_file_md5(file_path)
        slice_md5, content_md5_slice = self._get_file_slice_md5(file_path)

        return {
            'size': file_size,
            'content_md5': content_md5,
            'slice_md5': slice_md5,
            'content_md5_slice': content_md5_slice
        }
    def _get_file_block_list(self, file_path: str) -> List:
        block_list = []
        # 计算分片MD5列表
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                block_list.append(hashlib.md5(chunk).hexdigest())
        return block_list

    def rapid_upload(self, file_path: str, remote_path: str) -> Optional[Dict]:
        """秒传文件"""
        try:
            file_info = self._get_file_info(file_path)
            logger.info(f"秒传文件信息: size={file_info['size']}, md5={file_info['content_md5']}")

            url = f"{self.base_url}/xpan/file"
            params = {
                'method': 'rapidupload',
                'access_token': self.access_token
            }

            data = {
                'path': remote_path,
                'content-length': file_info['size'],
                'content-md5': file_info['content_md5'],
                'slice-md5': file_info['slice_md5'],
                'content-crc32': '0'  # CRC32可选，填0即可
            }

            logger.info(f"秒传请求参数: {data}")

            response = self.session.post(url, params=params, data=data, timeout=30)
            result = response.json()
            logger.info(f"秒传响应: {result}")

            if result.get('errno') == 0:
                logger.info(f"秒传成功: {remote_path}")
                return result
            else:
                logger.warning(f"秒传失败: {result.get('errmsg', '未知错误')}, errno: {result.get('errno')}")
                return None

        except Exception as e:
            logger.error(f"秒传请求异常: {e}")
            return None

    def precreate_upload(self, file_path: str, remote_path: str, block_list: list) -> dict[str, Any] | None:
        """预创建上传（分片上传）"""
        try:
            file_info = self._get_file_info(file_path)
            url = f"{self.base_url}/xpan/file"
            params = {
                'method': 'precreate',
                'access_token': self.access_token
            }

            data = {
                'path': remote_path,
                'size': file_info['size'],
                'isdir': 0,
                'autoinit': 1,
                'block_list': json.dumps(block_list),
                'rtype': 1  # 重命名策略：重命名
            }

            print(remote_path)
            logger.info(f"预创建请求: {data}")

            response = self.session.post(url, params=params, data=data, timeout=30)
            result = response.json()
            logger.info(f"预创建响应: {result}")

            if result.get('errno') == 0:
                return result
            else:
                logger.error(f"预创建失败: {result.get('errmsg')}, errno: {result.get('errno')}")
                return None

        except Exception as e:
            logger.error(f"预创建请求异常: {e}")
            return None

    def upload_slices(self, file_path: str, uploadid: str, remote_path: str) -> bool:
        """上传分片数据"""
        try:
            file_size = os.path.getsize(file_path)
            logger.info(f"开始上传分片，文件大小: {file_size}")

            with open(file_path, 'rb') as f, tqdm(
                    total=file_size, unit='B', unit_scale=True, desc="上传进度"
            ) as pbar:

                partseq = 0
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break

                    # 上传单个分片
                    url = "https://d.pcs.baidu.com/rest/2.0/pcs/superfile2"
                    params = {
                        'method': 'upload',
                        'access_token': self.access_token,
                        'type': 'tmpfile',
                        'path': remote_path,
                        'uploadid': uploadid,
                        'partseq': partseq
                    }

                    files = {'file': (f'part{partseq}', chunk)}

                    try:
                        response = self.session.post(url, params=params, files=files, timeout=60)
                        if response.status_code != 200:
                            logger.error(f"分片 {partseq} 上传失败: {response.status_code}")
                            return False
                        logger.debug(f"分片 {partseq} 上传成功")

                    except Exception as e:
                        logger.error(f"分片 {partseq} 上传异常: {e}")
                        return False

                    partseq += 1
                    pbar.update(len(chunk))

            logger.info("所有分片上传完成")
            return True

        except Exception as e:
            logger.error(f"分片上传过程异常: {e}")
            return False

    def create_file(self, size: int, remote_path: str, uploadid: str, block_list: list) -> Optional[Dict]:
        """创建文件（完成上传）"""
        try:
            url = f"{self.base_url}/xpan/file"
            params = {
                'method': 'create',
                'access_token': self.access_token
            }

            data = {
                'path': remote_path,
                'size': size,
                'isdir': 0,
                'block_list': json.dumps(block_list),
                'uploadid': uploadid,
            }

            logger.info(f"创建文件请求: {data}")

            response = self.session.post(url, params=params, data=data, timeout=30)
            result = response.json()
            logger.info(f"创建文件响应: {result}")

            if result.get('errno') == 0:
                return result
            else:
                logger.error(f"创建文件失败: {result.get('errmsg')}, errno: {result.get('errno')}")
                return None

        except Exception as e:
            logger.error(f"创建文件请求异常: {e}")
            return None

    def upload_file(self, file_path: str, remote_dir: str = "/apps/yt-download") -> Optional[Dict]:
        """主上传方法：先尝试秒传，失败则分片上传"""
        # 已下载文件所处的路径
        # print(f"已下载文件所处的路径:{file_path}")
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return None

        # 生成远程文件名（清理文件名中的特殊字符）
        filename = os.path.basename(file_path)
        # 生成block_list
        block_list = self._get_file_block_list(file_path)
        # 替换可能引起问题的字符
        safe_filename = filename.replace('?', '_').replace('*', '_').replace('"', '_')
        remote_path = f"{remote_dir}/{safe_filename}"
        remote_path = "/apps/yt-download/于朦胧母亲的声明系伪造｜教美国教友躲避ICE抓人的择吉时法｜周末玄学大课堂：鬼遮眼实例与科学解读｜出门给儿童叫魂的定向秘法｜或疯或死出马仙的可怜下场｜ [Esk-pbgFaBI].webm"

        logger.info(f"开始上传: {filename} -> {remote_path}")

        # 1. 尝试秒传
        rapid_result = self.rapid_upload(file_path, remote_path)
        if rapid_result:
            return rapid_result

        logger.info("秒传失败，开始分片上传...")

        # 2. 分片上传
        # 预创建
        precreate_result = self.precreate_upload(file_path, remote_path, block_list)
        if not precreate_result:
            return None

        uploadid = precreate_result.get('uploadid')
        if not uploadid:
            logger.error("获取uploadid失败")
            return None

        # 获取block_list（需要在precreate和create中使用相同的）
        # block_list = precreate_result.get('block_list', [])

        # 上传分片
        if not self.upload_slices(file_path, uploadid, remote_path):
            return None

        # 创建文件
        create_result = self.create_file(os.path.getsize(file_path), remote_path, uploadid, block_list)
        return create_result


def handle_upload(video_id: str, local_path: str, access_token: str) -> Dict:
    """处理上传请求"""
    logger.info(f"处理上传请求: video_id={video_id}, local_path={local_path}")

    # 检查访问令牌
    if not access_token or access_token == '你的访问令牌':
        return {
            'status': 'error',
            'message': '百度访问令牌未设置或无效',
            'videoId': video_id
        }

    uploader = BaiduPanUploader(access_token)

    try:
        result = uploader.upload_file(local_path)

        if result and result.get('errno') == 0:
            return {
                'status': 'success',
                'fs_id': result.get('fs_id', ''),
                'path': result.get('path', ''),
                'videoId': video_id,
                'message': '上传成功'
            }
        else:
            error_msg = result.get('errmsg', '上传失败') if result else '上传异常'
            errno = result.get('errno', '未知错误码') if result else '无响应'
            return {
                'status': 'error',
                'message': f'{error_msg} (错误码: {errno})',
                'videoId': video_id
            }

    except Exception as e:
        logger.error(f"上传过程异常: {e}")
        return {
            'status': 'error',
            'message': f'上传异常: {str(e)}',
            'videoId': video_id
        }

