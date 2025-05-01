import feedparser
import discord
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import os

# 環境変数の読み込み
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# クライアントの作成
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
scheduler = AsyncIOScheduler()

# RSS取得先
RSS_FEEDS = [
    "https://eiga.com/rss/news/",
    "https://natalie.mu/eiga/feed/news"
]

# 投稿済みリンクを記録
posted_links = set()

# ニュース収集＆投稿
async def fetch_and_post_news():
    channel = await client.fetch_channel(CHANNEL_ID)
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        print(f"Fetched {len(feed.entries)} entries from {url}")  # フィードの取得件数をログ表示
        if len(feed.entries) == 0:
            print(f"No entries found in feed: {url}")
        for entry in feed.entries[:10]:  # 最新の10件を取得
            if entry.link in posted_links:
                continue
            message = f"【映画ニュース】\nタイトル：{entry.title}\nリンク：{entry.link}"
            await channel.send(message)
            posted_links.add(entry.link)
            await asyncio.sleep(1)

# Bot起動時の処理
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    try:
        await fetch_and_post_news()  # 起動時に一度ニュースを投稿して確認する
        scheduler.add_job(fetch_and_post_news, 'interval', hours=3)
        scheduler.start()
    except Exception as e:
        print(f"Error occurred: {e}")

# ボットの実行
client.run(DISCORD_TOKEN)