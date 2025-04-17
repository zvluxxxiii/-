import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode

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

# ЛС → сообщение в группу с ID внутри текста
@dp.message(F.chat.type == "private", F.text)
async def handle_private_message(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без ника"
    text = message.text

    await bot.send_message(
        GROUP_ID,
        f"<b>✉️ Сообщение от @{username} (ID: <code>{user_id}</code>):</b>\n\n<i>{text}</i>"
    )

# Ответ из группы → бот ищет ID в тексте и шлёт в личку
@dp.message(F.chat.id == GROUP_ID, F.reply_to_message)
async def handle_group_reply(message: Message):
    reply_text = message.reply_to_message.text

    # Ищем ID: <code>123456789</code>
    if "ID: <code>" in reply_text:
        try:
            user_id = int(reply_text.split("ID: <code>")[1].split("</code>")[0])
            await bot.send_message(chat_id=user_id, text=message.text)
        except Exception as e:
            print(f"Ошибка при парсинге ID: {e}")
