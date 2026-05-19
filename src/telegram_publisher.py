"""Telegram 发布模块。

通过 Telegram Bot API 将格式化内容发送到指定频道。
支持 HTML 格式的图文消息。
"""

import logging
import os
import time

import requests

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org"


def _build_caption(repo: dict, summary: dict) -> str:
    """构建 Telegram 消息文本（HTML 格式）。"""
    hashtags = "  ".join(summary["hashtags"])
    stars = "⭐" * min(5, repo["stars"] // 1000 + 1)  # 根据 star 数显示星级

    caption = (
        f"\U0001f525 <b>{summary['title']}</b>\n\n"
        f"\U0001f3f7 {hashtags}\n\n"
        f"<blockquote>\U0001f4dd {summary['summary']}</blockquote>\n\n"
        f"\U0001f4ca Stars: {repo['stars']:,}  {stars}\n"
        f"\U0001f4c1 语言: {repo['language']}\n\n"
        f"\U0001f517 <a href=\"{repo['html_url']}\">直达项目 →</a>\n\n"
        f"<blockquote>\U0001f916 总结模型：DeepSeek ｜ ✍️ 一十八</blockquote>"
    )
    return caption


def publish_to_channel(repo: dict, summary: dict, photo_url: str | None) -> bool:
    """将一条项目推荐发布到 Telegram 频道。

    如果有图片则发送图片+文字标题，无图片则只发送文字。

    Args:
        repo: 仓库信息字典。
        summary: DeepSeek 总结字典。
        photo_url: Unsplash 图片 URL（可为 None）。

    Returns:
        bool: 是否发送成功。
    """
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    channel_id = os.environ.get("TELEGRAM_CHANNEL_ID", "")

    if not bot_token or not channel_id:
        raise ValueError("未设置 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHANNEL_ID")

    caption = _build_caption(repo, summary)

    try:
        if photo_url:
            # 发送带图片的消息
            resp = requests.post(
                f"{TELEGRAM_API}/bot{bot_token}/sendPhoto",
                json={
                    "chat_id": channel_id,
                    "photo": photo_url,
                    "caption": caption,
                    "parse_mode": "HTML",
                },
                timeout=90,
            )
        else:
            # 仅发送文字消息
            resp = requests.post(
                f"{TELEGRAM_API}/bot{bot_token}/sendMessage",
                json={
                    "chat_id": channel_id,
                    "text": caption,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False,
                },
                timeout=90,
            )

        resp.raise_for_status()
        logger.info("已发布到频道: %s", summary.get("title", repo["full_name"]))
        return True

    except requests.RequestException as e:
        logger.error("Telegram 发送失败: %s", e)
        if hasattr(e, "response") and e.response is not None:
            logger.error("响应内容: %s", e.response.text)
        return False


def publish_daily(repos_with_summaries: list[tuple[dict, dict, str | None]]) -> list[str]:
    """发布每日汇总到频道。

    Args:
        repos_with_summaries: [(repo, summary, photo_url), ...] 列表。

    Returns:
        list[str]: 成功发布的仓库全名列表。
    """
    success_names = []
    for repo, summary, photo_url in repos_with_summaries:
        if publish_to_channel(repo, summary, photo_url):
            success_names.append(repo["full_name"])
            time.sleep(2)
    logger.info("发布完成: 成功 %d/%d 条", len(success_names), len(repos_with_summaries))
    return success_names
