import asyncio
import time
import re
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode, ContentType
from aiogram.types import Message

# Токен и ID группы
TOKEN = "7307810781:AAFUOkaJr1YfbYrMVa6J6wV6xUuesG1zDF8"
GROUP_ID = -1002294772560

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Приветственное сообщение
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

# Антиспам
SPAM_LIMIT = 4
SPAM_SECONDS = 10
BLOCK_DURATION = 60 * 30  # 30 минут

user_activity = {}
user_blocked = {}

def is_spam(user_id):
    now = time.time()

    if user_id in user_blocked:
        if now < user_blocked[user_id]:
            return True
        else:
            del user_blocked[user_id]

    user_activity.setdefault(user_id, [])
    user_activity[user_id] = [t for t in user_activity[user_id] if now - t <= SPAM_SECONDS]
    user_activity[user_id].append(now)

    if len(user_activity[user_id]) > SPAM_LIMIT:
        user_blocked[user_id] = now + BLOCK_DURATION
        return True

    return False

@dp.message(F.text == "/start", F.chat.type == "private")
async def handle_start(message: Message):
    await message.answer(WELCOME_TEXT)

@dp.message(F.chat.type == "private")
async def handle_private(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без ника"
    header = f"Сообщение от @{username}"

    # Проверка на активный бан
    if user_id in user_blocked and time.time() < user_blocked[user_id]:
        await message.answer("⛔ Вы временно заблокированы за спам. Попробуйте позже.")
        return

    # Новый спам
    if is_spam(user_id):
        await message.answer("⛔ Вы были заблокированы за спам. Подождите 30 минут.")
        return

    # Пересылка разных типов
    if message.content_type == ContentType.TEXT:
        await bot.send_message(GROUP_ID, f"{header}\n\n{message.text}")
    elif message.content_type == ContentType.PHOTO:
        await bot.send_photo(GROUP_ID, message.photo[-1].file_id, caption=header)
    elif message.content_type == ContentType.STICKER:
        await bot.send_message(GROUP_ID, f"{header}\n\n(Стикер)")
        await bot.send_sticker(GROUP_ID, message.sticker.file_id)
    elif message.content_type == ContentType.VOICE:
        await bot.send_message(GROUP_ID, f"{header}\n\n(Голосовое)")
        await bot.send_voice(GROUP_ID, message.voice.file_id)
    else:
        await bot.send_message(GROUP_ID, f"{header}\n\n(Неподдерживаемый тип контента)")

# Ответы из группы в ЛС
@dp.message(F.chat.id == GROUP_ID, F.reply_to_message)
async def handle_group_reply(message: Message):
    original = message.reply_to_message
    content = original.text or original.caption or ""
    match = re.search(r"@([a-zA-Z0-9_]+).*ID:.*?(\d+)", content)
    if match:
        user_id = int(match.group(2))

        if message.content_type == ContentType.TEXT:
            await bot.send_message(chat_id=user_id, text=message.text)
        elif message.content_type == ContentType.STICKER:
            await bot.send_sticker(chat_id=user_id, sticker=message.sticker.file_id)
        elif message.content_type == ContentType.PHOTO:
            await bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=message.caption)
        elif message.content_type == ContentType.VOICE:
            await bot.send_voice(chat_id=user_id, voice=message.voice.file_id, caption=message.caption)

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

