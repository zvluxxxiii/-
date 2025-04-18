import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode, ContentType
import re
import time

TOKEN = "7307810781:AAFUOkaJr1YfbYrMVa6J6wV6xUuesG1zDF8"
GROUP_ID = -1002294772560

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Антиспам-хранилище
user_messages = {}
user_blocked_until = {}

SPAM_LIMIT = 4       # макс. сообщений
SPAM_INTERVAL = 10   # в течение секунд
BLOCK_TIME = 60 * 30 # блок на 30 минут

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

# Проверка спама
def is_spammer(user_id: int) -> bool:
    now = time.time()
    
    # Проверка на блок
    if user_id in user_blocked_until:
        if now < user_blocked_until[user_id]:
            return True
        else:
            del user_blocked_until[user_id]

    # Проверка активности
    timestamps = user_messages.get(user_id, [])
    timestamps = [t for t in timestamps if now - t < SPAM_INTERVAL]
    timestamps.append(now)
    user_messages[user_id] = timestamps

    if len(timestamps) > SPAM_LIMIT:
        user_blocked_until[user_id] = now + BLOCK_TIME
        return True

    return False

# Приём и отправка сообщений в группу
@dp.message(F.chat.type == "private")
async def handle_private(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без ника"
    header = f"Сообщение от @{username}"
    hidden_tag = f"<code>[user_id:{user_id}]</code>"

    if is_spammer(user_id):
        await message.answer("⏳ Вы временно заблокированы за слишком активные сообщения. Попробуйте позже.")
        return

    if message.content_type == ContentType.TEXT:
        await bot.send_message(GROUP_ID, f"{header}\n\n{message.text}\n\n{hidden_tag}")

    elif message.content_type == ContentType.PHOTO:
        await bot.send_photo(GROUP_ID, photo=message.photo[-1].file_id, caption=f"{header}\n\n{hidden_tag}")

    elif message.content_type == ContentType.STICKER:
        await bot.send_message(GROUP_ID, f"{header}\n\n(Стикер)\n\n{hidden_tag}")
        await bot.send_sticker(GROUP_ID, message.sticker.file_id)

    elif message.content_type == ContentType.VOICE:
        await bot.send_message(GROUP_ID, f"{header}\n\n(Голосовое)\n\n{hidden_tag}")
        await bot.send_voice(GROUP_ID, voice=message.voice.file_id)

    else:
        await bot.send_message(GROUP_ID, f"{header}\n\n(Неподдерживаемый тип)\n\n{hidden_tag}")

# Ответ из группы → в личку
@dp.message(F.chat.id == GROUP_ID, F.reply_to_message)
async def handle_group_reply(message: Message):
    original = message.reply_to_message
    full_text = original.text or original.caption or ""

    match = re.search(r"\[user_id:(\d+)\]", full_text)
    if match:
        user_id = int(match.group(1))

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
