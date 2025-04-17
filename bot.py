import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
import re

# Твой токен и ID группы
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

# Личное сообщение → в группу
@dp.message(F.chat.type == "private", F.text)
async def forward_to_group(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без ника"
    text = message.text

    await bot.send_message(
        GROUP_ID,
        f"<b>✉️ Сообщение от @{username} (ID: <code>{user_id}</code>):</b>\n\n<i>{text}</i>"
    )

# Ответ в группе → в ЛС
@dp.message(F.chat.id == GROUP_ID, F.reply_to_message)
async def reply_to_user(message: Message):
    replied = message.reply_to_message
    # Ищем user_id в тексте
    match = re.search(r'ID: <code>(\d+)</code>', replied.text)
    if match:
        user_id = int(match.group(1))
        try:
            await bot.send_message(chat_id=user_id, text=message.text)
        except Exception as e:
            await message.reply(f"Не удалось доставить сообщение пользователю.\nПричина: {e}")
