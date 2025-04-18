from antispam import is_banned, check_spam
import asyncio
import re
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode, ContentType
from aiogram.types import Message
from antispam import is_banned, check_spam  # подключение антиспама

# Токен и ID группы
TOKEN = "7307810781:AAFUOkaJr1YfbYrMVa6J6wV6xUuesG1zDF8"
GROUP_ID = -1002294772560

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

WELCOME_TEXT = """
⋆｡°✩₊
/ᐠ – ˕ –マ

Привет. Это “Эхо с небес”.
Если тебе тяжело — напиши.
Мы не судим, не исправляем, не умничаем.
Мы просто рядом.

✩ ꒰՞•ﻌ•՞꒱
Ты не один.
Ты не одна.
И это место — для тебя.

⭒ﾟ･｡☆･｡
Ответ может прийти не сразу,
но тебя обязательно услышат.

Чтобы написать конкретному админу,
укажи хештег в конце сообщения — например: #мики
"""

@dp.message(F.text == "/start", F.chat.type == "private")
async def handle_start(message: Message):
    await message.answer(WELCOME_TEXT)

@dp.message(F.chat.type == "private")
async def handle_user_message(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без ника"
    header = f"<b>✉️ Сообщение от @{username}:</b>"

    # антиспам
    if is_banned(user_id):
        await message.answer("⛔ Вы временно заблокированы за спам. Подождите 30 минут.")
        return

    if check_spam(user_id):
        await message.answer("⛔ Вы были заблокированы за спам. Подождите 30 минут.")
        return

    # обработка контента
    if message.content_type == ContentType.TEXT:
        await bot.send_message(GROUP_ID, f"{header}\n\n<em>{message.text}</em>")

    elif message.content_type == ContentType.PHOTO:
        await bot.send_photo(GROUP_ID, message.photo[-1].file_id, caption=header)

    elif message.content_type == ContentType.STICKER:
        await bot.send_message(GROUP_ID, f"{header}\n\n(Стикер)")
        await bot.send_sticker(GROUP_ID, message.sticker.file_id)

    elif message.content_type == ContentType.VOICE:
        await bot.send_message(GROUP_ID, f"{header}\n\n(Голосовое)")
        await bot.send_voice(GROUP_ID, message.voice.file_id)

    else:
        await bot.send_message(GROUP_ID, f"{header}\n\n(Неподдерживаемый тип)")

@dp.message(F.chat.id == GROUP_ID, F.reply_to_message)
async def reply_to_user(message: Message):
    original = message.reply_to_message
    content = original.text or original.caption or ""
    match = re.search(r"@([a-zA-Z0-9_]+)", content)
    if not match:
        return

    username = match.group(1)

    # можно заменить на хранение id, если будет стабильнее
    # но сейчас просто отправляется сообщение обратно
    if message.content_type == ContentType.TEXT:
        await message.reply("✉️ Ответ отправлен.")
    # (Можно добавить логику ответа в ЛС, если будет храниться ID)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
