import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
import re

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

# Обработка команды /start
@dp.message(F.text == "/start", F.chat.type == "private")
async def handle_start(message: Message):
    await message.answer(WELCOME_TEXT)

# Пересылка личных сообщений в группу
@dp.message(F.chat.type == "private", F.text)
async def handle_private(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без ника"
    text = message.text

    await bot.send_message(
        GROUP_ID,
        f"<b>✉️ Сообщение от @{username} (ID: <code>{user_id}</code>):</b>\n\n<i>{text}</i>\n\n[user_id:{user_id}]"
    )

# Ответ из группы обратно в ЛС пользователя
@dp.message(F.chat.id == GROUP_ID, F.reply_to_message)
async def handle_group_reply(message: Message):
    original_text = message.reply_to_message.text

    match = re.search(r"\[user_id:(\d+)\]", original_text)
    if match:
        user_id = int(match.group(1))
        await bot.send_message(chat_id=user_id, text=message.text)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
