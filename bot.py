import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode

# ТВОЙ токен и ID группы
TOKEN = "7307810781:AAFUOkaJr1YfbYrMVa6J6wV6xUuesG1zDF8"
GROUP_ID = -1002294772560

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Память: ID сообщения в группе → ID пользователя
user_links = {}

# Приветствие
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

# Отправка приветствия на /start
@dp.message(F.text == "/start", F.chat.type == "private")
async def handle_start(message: Message):
    await message.answer(WELCOME_TEXT)

# Пересылка ЛС → в группу
@dp.message(F.chat.type == "private", F.text)
async def handle_private_message(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без ника"
    text = message.text

    forwarded = await bot.send_message(
        GROUP_ID,
        f"<b>✉️ Сообщение от @{username} (ID: <code>{user_id}</code>):</b>\n\n<i>{text}</i>"
    )
    user_links[forwarded.message_id] = user_id

# Ответ из группы → в личку
@dp.message(F.chat.id == GROUP_ID, F.reply_to_message)
async def handle_group_reply(message: Message):
    replied_id = message.reply_to_message.message_id

    if replied_id in user_links:
        user_id = user_links[replied_id]
        await bot.send_message(chat_id=user_id, text=message.text)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
