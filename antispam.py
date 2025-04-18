import time

SPAM_LIMIT = 4            # сообщений
SPAM_SECONDS = 10         # за сколько секунд
BLOCK_DURATION = 60 * 30  # бан на 30 минут

user_activity = {}
user_blocked = {}

def is_banned(user_id):
    now = time.time()
    if user_id in user_blocked:
        if now < user_blocked[user_id]:
            return True
        else:
            del user_blocked[user_id]
    return False

def check_spam(user_id):
    now = time.time()
    user_activity.setdefault(user_id, [])
    user_activity[user_id] = [t for t in user_activity[user_id] if now - t <= SPAM_SECONDS]
    user_activity[user_id].append(now)

    if len(user_activity[user_id]) > SPAM_LIMIT:
        user_blocked[user_id] = now + BLOCK_DURATION
        return True
    return False
