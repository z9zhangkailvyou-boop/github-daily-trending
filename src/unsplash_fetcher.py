"""Unsplash 图片搜索模块。

根据关键词在 Unsplash 上搜索与项目主题匹配的配图。
"""

import logging
import os

import requests

logger = logging.getLogger(__name__)

UNSPLASH_API = "https://api.unsplash.com"


def search_photo(keyword: str) -> str | None:
    """根据关键词搜索 Unsplash 图片，返回第一张图片的 URL。

    Args:
        keyword: 英文搜索关键词。

    Returns:
        图片 URL 字符串，搜索失败返回 None。
    """
    access_key = os.environ.get("UNSPLASH_ACCESS_KEY", "")
    if not access_key:
        logger.warning("未设置 UNSPLASH_ACCESS_KEY，跳过图片搜索")
        return None

    headers = {"Authorization": f"Client-ID {access_key}"}
    params = {
        "query": keyword,
        "per_page": 1,
        "orientation": "landscape",
    }

    logger.info("搜索 Unsplash 图片: keyword=%s", keyword)
    try:
        resp = requests.get(f"{UNSPLASH_API}/search/photos", headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        if results:
            url = results[0]["urls"]["regular"]
            logger.info("图片搜索成功: %s", url)
            return url
        else:
            logger.warning("未找到匹配图片: %s", keyword)
            return None
    except requests.RequestException as e:
        logger.error("Unsplash API 请求失败: %s", e)
        return None
