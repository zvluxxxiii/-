import asyncio
import time
import re
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode, ContentType
from aiogram.types import Message

TOKEN = "7307810781:AAFUOkaJr1YfbYrMVa6J6wV6xUuesG1zDF8"
GROUP_ID = -1002294772560

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

user_activity = {}
user_blocked = {}

SPAM_LIMIT = 4
SPAM_SECONDS = 10
BLOCK_DURATION = 60 * 30

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

def is_spammer(user_id: int) -> bool:
    now = time.time()

    if user_id in user_blocked:
        if now < user_blocked[user_id]:
            return True
        else:
            del user_blocked[user_id]

    user_activity.setdefault(user_id, [])
    user_activity[user_id] = [t for t in user_activity[user_id] if now - t < SPAM_SECONDS]
    user_activity[user_id].append(now)

    if len(user_activity[user_id]) > SPAM_LIMIT:
        user_blocked[user_id] = now + BLOCK_DURATION
        asyncio.create_task(bot.send_message(GROUP_ID, f"⚠️ Пользователь <code>{user_id}</code> автоматически заблокирован на 30 минут за спам."))
        return True

    return False

# ЛС → группа
@dp.message(F.chat.type == "private")
async def handle_private(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без ника"
    header = f"Сообщение от @{username}"
    hidden = f"<a href='tg://user?id={user_id}'>\u2063</a>"  # невидимый user_id

    if is_spammer(user_id):
        await message.answer("⏳ Вы временно заблокированы за спам. Подождите немного.")
        return

    if message.content_type == ContentType.TEXT:
        await bot.send_message(GROUP_ID, f"{header}\n\n{message.text}{hidden}")

    elif message.content_type == ContentType.PHOTO:
        await bot.send_photo(GROUP_ID, message.photo[-1].file_id, caption=f"{header}\n\n{hidden}")

    elif message.content_type == ContentType.STICKER:
        await bot.send_message(GROUP_ID, f"{header}\n\n(Стикер){hidden}")
        await bot.send_sticker(GROUP_ID, message.sticker.file_id)

    elif message.content_type == ContentType.VOICE:
        await bot.send_message(GROUP_ID, f"{header}\n\n(Голосовое){hidden}")
        await bot.send_voice(GROUP_ID, message.voice.file_id)

    else:
        await bot.send_message(GROUP_ID, f"{header}\n\n(Сообщение){hidden}")

# Ответ из группы → ЛС
@dp.message(F.chat.id == GROUP_ID, F.reply_to_message)
async def handle_group_reply(message: Message):
    original = message.reply_to_message
    text = original.text or original.caption or ""
    match = re.search(r"tg://user\?id=(\d+)", text)
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

# Команда: /бан @юзер
@dp.message(F.chat.id == GROUP_ID, F.text.startswith("/бан"))
async def manual_ban(message: Message):
    match = re.search(r"@?(\w+)", message.text)
    if match:
        username = match.group(1)
        # найти user_id из reply
        if message.reply_to_message:
            reply = message.reply_to_message.text or message.reply_to_message.caption
            id_match = re.search(r"tg://user\?id=(\d+)", reply)
            if id_match:
                user_id = int(id_match.group(1))
                user_blocked[user_id] = time.time() + BLOCK_DURATION
                await message.reply(f"⛔ Пользователь <code>{user_id}</code> заблокирован вручную на 30 минут.")

# Команда: /разбан @юзер
@dp.message(F.chat.id == GROUP_ID, F.text.startswith("/разбан"))
async def manual_unban(message: Message):
    if message.reply_to_message:
        reply = message.reply_to_message.text or message.reply_to_message.caption
        id_match = re.search(r"tg://user\?id=(\d+)", reply)
        if id_match:
            user_id = int(id_match.group(1))
            if user_id in user_blocked:
                del user_blocked[user_id]
                await message.reply(f"✅ Пользователь <code>{user_id}</code> разблокирован.")
            else:
                await message.reply("Этот пользователь не в бане.")

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

