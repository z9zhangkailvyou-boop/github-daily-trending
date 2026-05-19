"""推送历史追踪模块。

维护一个 JSON 文件记录哪些仓库已经推送过，防止一周内重复推送。
"""

import json
import logging
import os
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

HISTORY_FILE = "data/sent_repos.json"
RETENTION_DAYS = 7


def _ensure_dir() -> None:
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)


def load_sent_repos() -> dict[str, str]:
    """加载已推送仓库记录，自动清理超过 7 天的条目。

    Returns:
        dict: { "owner/repo": "2026-05-19", ... }
    """
    if not os.path.exists(HISTORY_FILE):
        return {}

    try:
        with open(HISTORY_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        logger.warning("历史文件损坏，将重新创建")
        return {}

    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    cutoff_str = cutoff.strftime("%Y-%m-%d")

    cleaned = {k: v for k, v in data.items() if v >= cutoff_str}
    removed = len(data) - len(cleaned)
    if removed:
        logger.info("清理了 %d 条过期记录", removed)

    return cleaned


def save_sent_repos(repos: dict[str, str]) -> None:
    """保存推送记录到文件。"""
    _ensure_dir()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(repos, f, ensure_ascii=False, indent=2)


def mark_as_sent(full_names: list[str]) -> None:
    """将一批仓库标记为已推送。

    Args:
        full_names: 仓库全名列表，如 ["owner/repo1", "owner/repo2"]
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    repos = load_sent_repos()
    for name in full_names:
        repos[name] = today
    save_sent_repos(repos)
    logger.info("已标记 %d 个仓库为已推送", len(full_names))
