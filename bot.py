import os
import yt_dlp
from collections import defaultdict
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")
CHANNEL = "@infocenterpro"

user_limits = defaultdict(int)
MAX_VIDEOS_PER_DAY = 4


async def is_subscribed(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """✨⚜️ Добро пожаловать 💾👋

📹 Отправь ссылку на видео 🎥

📌 Подпишись на канал:
https://t.me/infocenterpro
"""
    await update.message.reply_text(text)


def download_video(url):
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'best[ext=mp4]/best',
        'noplaylist': True,
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    url = update.message.text

    # Проверка подписки
    if not await is_subscribed(context.bot, user_id):
        await update.message.reply_text(
            "❗ Подпишись на канал:\nhttps://t.me/infocenterpro"
        )
        return

    # Проверка ссылки
    if not url.startswith("http"):
        await update.message.reply_text("📎 Отправь ссылку на видео")
        return

    # Лимит
    if user_limits[user_id] >= MAX_VIDEOS_PER_DAY:
        await update.message.reply_text(
            "⛔ Лимит исчерпан.\n\n💎 Оформи платную подписку."
        )
        return

    await update.message.reply_text("⏳ Скачиваю видео...")

    try:
        download_video(url)

        # ищем файл
        video_file = None
        for file in os.listdir():
            if file.startswith("video"):
                video_file = file
                break

        if video_file:
            with open(video_file, "rb") as video:
                await update.message.reply_video(video)

            os.remove(video_file)

        user_limits[user_id] += 1

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    app.run_polling()


if __name__ == "__main__":
    main()
