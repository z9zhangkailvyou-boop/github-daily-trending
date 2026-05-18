# 🤖 GitHub 每日开源精选

> 每天早上 9:00，一个机器人替你逛遍 GitHub，挑出最火的开源项目，用 AI 写成中文推荐，配上精美图片，推到你的 Telegram 频道。

## ✨ 它能干嘛

每天自动完成下面这 4 件事：

| 步骤 | 干嘛的 | 用的啥 |
|------|--------|--------|
| 🔍 发现 | 从 GitHub 搜出过去 3 天星星涨得最猛的新项目 | GitHub Search API |
| 🧠 总结 | 把英文项目信息变成中文标题、简介、标签 | DeepSeek AI |
| 🖼 配图 | 根据项目主题搜一张高颜值配图 | Unsplash |
| 📬 发布 | 排版成好看的图文消息推到 Telegram 频道 | Telegram Bot |

## 📸 效果预览

每条推送长这样：

```
🔥 Zero：AI原生后端开发框架

🏷 #AI  #开源  #TypeScript  #后端开发

┃ 📝 Vercel 推出的 Zero 是一个 AI 原生的后端开发框架，
┃     让开发者可以用自然语言描述需求，自动生成类型安全的后端 API。

📊 Stars: 3,241  ⭐⭐⭐
📁 语言: TypeScript

🔗 直达项目 →

┃ 🤖 总结模型：DeepSeek ｜ ✍️ 一十八
```

## 🚀 快速开始

### 1. 准备四个东西

| 你需要 | 去哪儿弄 |
|--------|----------|
| DeepSeek API Key | [platform.deepseek.com](https://platform.deepseek.com/api_keys) |
| Telegram Bot Token | 找 [@BotFather](https://t.me/BotFather) 创建一个 |
| Telegram 频道 ID | 把你的 Bot 拉进频道，设为管理员 |
| Unsplash Access Key | [unsplash.com/developers](https://unsplash.com/developers) 注册应用 |

### 2. Fork 这个仓库

点右上角 Fork → 然后去 Settings → Secrets and variables → Actions，添加四个 Secrets：

```
DEEPSEEK_API_KEY    你的 DeepSeek 密钥
TELEGRAM_BOT_TOKEN  你的 Telegram Bot Token
TELEGRAM_CHANNEL_ID 你的频道 ID（如 @mychannel）
UNSPLASH_ACCESS_KEY 你的 Unsplash 密钥
```

### 3. 完事儿

什么都不用管了。每天早上 9:00（北京时间），GitHub Actions 会自动跑一轮。

> 想马上看效果？去 Actions 标签页 → 点 "GitHub 每日开源项目精选" → Run workflow。

## 🏗 本地跑

```bash
git clone https://github.com/你的用户名/github-daily-trending.git
cd github-daily-trending
pip install -r requirements.txt

# 创建 .env 填好四个环境变量
cp .env.example .env

python -m src.main
```

## 🧩 项目结构

```
.
├── .github/workflows/daily-post.yml   # 定时触发 + 手动触发
├── src/
│   ├── main.py                        # 主流程编排
│   ├── github_fetcher.py              # ① 抓热门仓库
│   ├── deepseek_summarizer.py         # ② AI 写中文推荐
│   ├── unsplash_fetcher.py            # ③ 搜配图
│   └── telegram_publisher.py          # ④ 发频道
├── requirements.txt
└── .env.example
```

## ⚙️ 想自定义？

- **改发布时间**：编辑 `.github/workflows/daily-post.yml` 里的 cron 表达式
- **改抓取数量**：改 `src/github_fetcher.py` 里的 `TOP_N`
- **改 AI 模型**：改 `src/deepseek_summarizer.py` 里的 `MODEL`
- **改消息样式**：改 `src/telegram_publisher.py` 里的 `_build_caption`

## 📝 署名

文案由 DeepSeek AI 生成，排版与工程由 **一十八** 完成。
