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


def fetch_trending_repos(exclude: set[str] | None = None) -> list[dict]:
    """抓取 GitHub 上近期最热门的开源仓库，返回 Top N。

    Args:
        exclude: 需要排除的仓库全名集合，如 {"owner/repo1", ...}。

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
    exclude = exclude or set()
    since = _date_n_days_ago(CREATED_DAYS)
    # 多抓一些以应对部分仓库被过滤
    fetch_count = TOP_N + len(exclude) + 3
    params = {
        "q": f"created:>={since} stars:>={MIN_STARS}",
        "sort": "stars",
        "order": "desc",
        "per_page": min(fetch_count, 30),
    }
    headers = {"Accept": "application/vnd.github+json"}

    logger.info("搜索 GitHub 仓库: since=%s, min_stars=%d", since, MIN_STARS)
    resp = requests.get(f"{GITHUB_API}/search/repositories", params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    repos = []
    for item in data.get("items", []):
        full_name = item["full_name"]
        if full_name in exclude:
            logger.info("跳过已推送: %s", full_name)
            continue
        repos.append({
            "full_name": full_name,
            "description": item.get("description") or "",
            "html_url": item["html_url"],
            "stars": item["stargazers_count"],
            "language": item.get("language") or "Unknown",
            "topics": item.get("topics", []),
            "created_at": item["created_at"],
        })
        if len(repos) >= TOP_N:
            break

    logger.info("获取到 %d 个新仓库（跳过 %d 个）", len(repos), len(exclude))
    return repos
