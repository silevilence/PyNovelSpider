from typing import Dict, Optional
import requests
import os


def get_webpage(
    url: str,
    proxy: str = "",
    cookies: dict = {},
    headers: Optional[Dict[str, str]] = None,
    max_retry=3,
) -> Optional[str]:
    """获取网页内容"""
    proxies = {} if not proxy.strip() else {"http": proxy, "https": proxy}

    if headers is None:
        headers = {}
    if headers.get("User-Agent") is None:
        headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        )

    tried = 0
    while tried < max_retry:
        try:
            resp = requests.get(url, proxies=proxies, cookies=cookies, headers=headers)
            if resp.status_code == 200:
                return resp.text
        except Exception as e:
            print(f"Error: {e}")
        tried += 1
    return None


def download_image(
    url: str,
    save_path: str,
    proxy: str = "",
    cookies: dict = {},
    headers: Optional[Dict[str, str]] = None,
    max_retry=3,
) -> bool:
    """下载图片到指定路径
    :param url: 图片URL
    :param save_path: 保存路径
    :param proxy: 代理
    :param cookies: cookies
    :param headers: 请求头
    :param max_retry: 最大重试次数
    :return: 是否成功
    """
    proxies = {} if not proxy.strip() else {"http": proxy, "https": proxy}

    if headers is None:
        headers = {}
    if headers.get("User-Agent") is None:
        headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        )

    tried = 0
    while tried < max_retry:
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            resp = requests.get(url, proxies=proxies, cookies=cookies, headers=headers)
            if resp.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(resp.content)
                return True
        except Exception as e:
            print(f"Error downloading image: {e}")
        tried += 1
    return False
