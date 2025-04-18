import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode, ContentType
import re

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

# /start → приветствие
@dp.message(F.text == "/start", F.chat.type == "private")
async def handle_start(message: Message):
    await message.answer(WELCOME_TEXT)

# Пересылка сообщений в группу (с сохранением user_id внутри текста)
@dp.message(F.chat.type == "private")
async def handle_private(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без ника"
    hidden_id = f"[user_id:{user_id}]"  # эта строка останется внизу для пересылки

    header = f"Сообщение от @{username}"

    if message.content_type == ContentType.TEXT:
        await bot.send_message(GROUP_ID, f"{header}\n\n{message.text}\n\n{hidden_id}")

    elif message.content_type == ContentType.PHOTO:
        await bot.send_photo(GROUP_ID, photo=message.photo[-1].file_id, caption=f"{header}\n\n{hidden_id}")

    elif message.content_type == ContentType.STICKER:
        await bot.send_message(GROUP_ID, f"{header}\n\n(Стикер)\n\n{hidden_id}")
        await bot.send_sticker(GROUP_ID, message.sticker.file_id)

    else:
        await bot.send_message(GROUP_ID, f"{header}\n\n(Неподдерживаемый тип сообщения)\n\n{hidden_id}")

# Ответ из группы обратно в ЛС
@dp.message(F.chat.id == GROUP_ID, F.reply_to_message)
async def handle_group_reply(message: Message):
    original = message.reply_to_message
    full_text = original.text or original.caption or ""

    match = re.search(r"\[user_id:(\d+)\]", full_text)
    if match:
        user_id = int(match.group(1))
        await bot.send_message(chat_id=user_id, text=message.text)

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

