"""主入口模块。

编排整个流程：
1. 抓取 GitHub 热门仓库
2. DeepSeek 生成中文总结
3. Unsplash 搜索配图
4. Telegram 发布到频道
"""

import logging
import os
import sys

from dotenv import load_dotenv

from . import github_fetcher, deepseek_summarizer, unsplash_fetcher, telegram_publisher, history

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> int:
    """运行一次完整的每日推荐流程。返回退出码。"""
    logger.info("===== GitHub 每日开源项目精选 开始 =====")

    # 0. 加载推送历史，排除 7 天内已推送的仓库
    sent_repos = history.load_sent_repos()
    exclude = set(sent_repos.keys())
    if exclude:
        logger.info("已加载 %d 条历史记录，将跳过已推送仓库", len(exclude))

    # 1. 抓取热门仓库
    try:
        repos = github_fetcher.fetch_trending_repos(exclude=exclude)
    except Exception as e:
        logger.error("抓取 GitHub 仓库失败: %s", e)
        return 1

    if not repos:
        logger.warning("未找到符合条件的仓库，退出")
        return 0

    logger.info("抓取到 %d 个热门仓库，开始 AI 总结", len(repos))

    # 2 & 3. 对每个仓库：DeepSeek 总结 + Unsplash 搜图
    results = []
    for repo in repos:
        # DeepSeek 总结
        try:
            summary = deepseek_summarizer.summarize_repo(repo)
        except Exception as e:
            logger.error("DeepSeek 总结失败 [%s]: %s，跳过", repo["full_name"], e)
            continue

        # Unsplash 搜图
        try:
            photo_url = unsplash_fetcher.search_photo(summary.get("image_keyword", repo["language"]))
        except Exception as e:
            logger.error("Unsplash 搜索失败 [%s]: %s，使用无图模式", repo["full_name"], e)
            photo_url = None

        results.append((repo, summary, photo_url))
        logger.info("处理完成: %s → 「%s」", repo["full_name"], summary.get("title", ""))

    if not results:
        logger.warning("没有任何项目成功处理，退出")
        return 0

    # 4. 发布到 Telegram
    try:
        sent_names = telegram_publisher.publish_daily(results)
    except Exception as e:
        logger.error("Telegram 发布失败: %s", e)
        return 1

    # 5. 记录已成功推送的仓库
    if sent_names:
        history.mark_as_sent(sent_names)

    logger.info("===== 完成: 成功发布 %d/%d 条 =====", len(sent_names), len(results))
    return 0 if len(sent_names) > 0 else 1


if __name__ == "__main__":
    load_dotenv()
    sys.exit(main())
