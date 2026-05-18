"""DeepSeek AI 总结模块。

调用 DeepSeek Chat API 对 GitHub 仓库信息进行中文总结，
生成标题、简介、标签和图片搜索关键词。
"""

import json
import logging
import os

import requests

logger = logging.getLogger(__name__)

DEEPSEEK_API = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"

SYSTEM_PROMPT = """你是一个专业的技术编辑，负责为 GitHub 开源项目撰写推荐文案。

对于每个项目，你需要根据我提供的仓库信息，输出严格的 JSON 格式：

{
  "title": "中文项目标题（15字以内，吸引眼球但不标题党）",
  "summary": "中文项目简介（80-120字，说明项目解决了什么问题、有何亮点）",
  "hashtags": ["Tag1", "Tag2", "Tag3", "Tag4"],
  "image_keyword": "用于在 Unsplash 搜索配图的英文关键词（1-3个单词，与项目主题强相关）"
}

要求：
- title 必须简洁有力，能让读者一眼就想点进去
- summary 要说清楚项目是干什么的、为什么值得关注
- hashtags 生成 3-5 个中英文混合标签，带 # 前缀（如 #AI #开源 #Python）
- image_keyword 必须是纯英文，选择最能代表项目视觉主题的词汇
- 只输出 JSON，不要包含其他任何文字或 markdown 标记"""


def summarize_repo(repo: dict) -> dict:
    """使用 DeepSeek 对单个仓库进行中文总结。

    Args:
        repo: github_fetcher 返回的仓库信息字典。

    Returns:
        dict: 包含 title, summary, hashtags, image_keyword。
    """
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        raise ValueError("未设置 DEEPSEEK_API_KEY 环境变量")

    # 构建用户消息
    topics_str = ", ".join(repo["topics"][:8]) if repo["topics"] else "无"
    user_message = f"""请为以下 GitHub 开源项目撰写推荐：

仓库名称: {repo['full_name']}
描述: {repo['description'] or '无描述'}
语言: {repo['language']}
Stars: {repo['stars']}
标签: {topics_str}"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.7,
        "max_tokens": 600,
    }

    logger.info("正在为 %s 生成 DeepSeek 总结...", repo["full_name"])
    resp = requests.post(DEEPSEEK_API, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    content = data["choices"][0]["message"]["content"].strip()

    # 清理可能的 markdown 代码块标记
    if content.startswith("```"):
        content = content.removeprefix("```json").removeprefix("```").strip()
    if content.endswith("```"):
        content = content[:-3].strip()

    result = json.loads(content)
    logger.info("总结生成成功: %s", result.get("title", ""))
    return result
