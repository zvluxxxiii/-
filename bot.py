import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.enums import ParseMode, ContentType
import re
import time

TOKEN = "7307810781:AAFUOkaJr1YfbYrMVa6J6wV6xUuesG1zDF8"
GROUP_ID = -1002294772560

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# user_id: [timestamps]
user_message_times = {}
user_blocked_until = {}

SPAM_LIMIT = 4  # сообщений
SPAM_INTERVAL = 10  # секунд
BLOCK_DURATION = 60 * 30  # 30 минут

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

# Приветствие
@dp.message(F.text == "/start", F.chat.type == "private")
async def handle_start(message: Message):
    await message.answer(WELCOME_TEXT)

# Проверка спама
def is_spamming(user_id: int) -> bool:
    now = time.time()
    if user_id in user_blocked_until:
        if now < user_blocked_until[user_id]:
            return True
        else:
            del user_blocked_until[user_id]

    timestamps = user_message_times.get(user_id, [])
    timestamps = [t for t in timestamps if now - t < SPAM_INTERVAL]
    timestamps.append(now)
    user_message_times[user_id] = timestamps

    if len(timestamps) > SPAM_LIMIT:
        user_blocked_until[user_id] = now + BLOCK_DURATION
        return True
    return False

# ЛС → группа (любой тип)
@dp.message(F.chat.type == "private")
async def handle_private_message(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без ника"

    if is_spamming(user_id):
        await message.answer("⏳ Вы слишком активно пишете. Подождите немного, пожалуйста.")
        return

    caption = f"Сообщение от @{username}\n[user_id:{user_id}]"

    if message.content_type == ContentType.TEXT:
        await bot.send_message(GROUP_ID, f"{caption}\n\n{message.text}")

    elif message.content_type == ContentType.PHOTO:
        await bot.send_photo(GROUP_ID, photo=message.photo[-1].file_id, caption=caption)

    elif message.content_type == ContentType.STICKER:
        await bot.send_sticker(GROUP_ID, sticker=message.sticker.file_id)

    elif message.content_type == ContentType.DOCUMENT:
        await bot.send_document(GROUP_ID, document=message.document.file_id, caption=caption)

    elif message.content_type == ContentType.VOICE:
        await bot.send_voice(GROUP_ID, voice=message.voice.file_id, caption=caption)

    else:
        await bot.send_message(GROUP_ID, f"{caption}\n(отправлен неизвестный тип сообщения)")

# Ответ из группы → ЛС
@dp.message(F.chat.id == GROUP_ID, F.reply_to_message)
async def handle_group_reply(message: Message):
    reply_text = message.reply_to_message.text or message.reply_to_message.caption
    match = re.search(r"\[user_id:(\d+)\]", reply_text)
    if match:
        user_id = int(match.group(1))
        if message.content_type == ContentType.TEXT:
            await bot.send_message(chat_id=user_id, text=message.text)
        elif message.content_type == ContentType.STICKER:
            await bot.send_sticker(chat_id=user_id, sticker=message.sticker.file_id)
        elif message.content_type == ContentType.PHOTO:
            await bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=message.caption)
        elif message.content_type == ContentType.DOCUMENT:
            await bot.send_document(chat_id=user_id, document=message.document.file_id, caption=message.caption)
        elif message.content_type == ContentType.VOICE:
            await bot.send_voice(chat_id=user_id, voice=message.voice.file_id, caption=message.caption)
