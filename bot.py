import asyncio
import re
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode, ContentType
from aiogram.types import Message
from antispam import is_banned, check_spam

TOKEN = "7307810781:AAFUOkaJr1YfbYrMVa6J6wV6xUuesG1zDF8"
GROUP_ID = -1002294772560

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Хранилище: message_id в группе → user_id
message_links = {}

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
async def handle_private(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без ника"
    header = f"Сообщение от @{username}"

    if is_banned(user_id):
        await message.answer("⛔ Вы временно заблокированы за спам.")
        return

    if check_spam(user_id):
        await message.answer("⚠️ Вы были заблокированы за спам на 30 минут.")
        return

    # Пересылка сообщений в группу
    if message.content_type == ContentType.TEXT:
        sent = await bot.send_message(GROUP_ID, f"{header}\n\n{message.text}")
    elif message.content_type == ContentType.PHOTO:
        sent = await bot.send_photo(GROUP_ID, message.photo[-1].file_id, caption=header)
    elif message.content_type == ContentType.STICKER:
        await bot.send_message(GROUP_ID, f"{header}\n\n(Стикер)")
        sent = await bot.send_sticker(GROUP_ID, message.sticker.file_id)
    elif message.content_type == ContentType.VOICE:
        await bot.send_message(GROUP_ID, f"{header}\n\n(Голосовое)")
        sent = await bot.send_voice(GROUP_ID, message.voice.file_id)
    else:
        sent = await bot.send_message(GROUP_ID, f"{header}\n\n(Неподдерживаемый тип)")

    # Сохраняем связь: id сообщения в группе → user_id
    message_links[sent.message_id] = user_id

@dp.message(F.chat.id == GROUP_ID, F.reply_to_message)
async def handle_group_reply(message: Message):
    original_id = message.reply_to_message.message_id
    if original_id not in message_links:
        await message.reply("⚠️ Не удалось определить пользователя. Ответь именно на сообщение от бота.")
        return

    user_id = message_links[original_id]

    if message.content_type == ContentType.TEXT:
        await bot.send_message(user_id, message.text)
    elif message.content_type == ContentType.STICKER:
        await bot.send_sticker(user_id, message.sticker.file_id)
    elif message.content_type == ContentType.PHOTO:
        await bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
    elif message.content_type == ContentType.VOICE:
        await bot.send_voice(user_id, message.voice.file_id)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
