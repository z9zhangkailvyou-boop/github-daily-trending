"""GitHub 热门仓库抓取模块。

使用 GitHub Search API 搜索近期创建的高星标仓库。
"""

import logging
from datetime import datetime, timedelta, timezone

import requests

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
# 搜索近3天创建、stars >= 50 的仓库，按 stars 降序
CREATED_DAYS = 3
MIN_STARS = 50
TOP_N = 5


def _date_n_days_ago(n: int) -> str:
    """返回 n 天前的日期字符串，格式 YYYY-MM-DD。"""
    dt = datetime.now(timezone.utc) - timedelta(days=n)
    return dt.strftime("%Y-%m-%d")


def fetch_trending_repos() -> list[dict]:
    """抓取 GitHub 上近期最热门的开源仓库，返回 Top N。

    Returns:
        list[dict]: 每个仓库包含:
            - full_name: 仓库全名 (owner/repo)
            - description: 仓库描述
            - html_url: GitHub 地址
            - stars: star 数量
            - language: 主要编程语言
            - topics: 主题标签列表
            - created_at: 创建时间
    """
    since = _date_n_days_ago(CREATED_DAYS)
    params = {
        "q": f"created:>={since} stars:>={MIN_STARS}",
        "sort": "stars",
        "order": "desc",
        "per_page": TOP_N,
    }
    headers = {"Accept": "application/vnd.github+json"}

    logger.info("搜索 GitHub 仓库: since=%s, min_stars=%d", since, MIN_STARS)
    resp = requests.get(f"{GITHUB_API}/search/repositories", params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    repos = []
    for item in data.get("items", []):
        repos.append({
            "full_name": item["full_name"],
            "description": item.get("description") or "",
            "html_url": item["html_url"],
            "stars": item["stargazers_count"],
            "language": item.get("language") or "Unknown",
            "topics": item.get("topics", []),
            "created_at": item["created_at"],
        })

    logger.info("获取到 %d 个热门仓库", len(repos))
    return repos
