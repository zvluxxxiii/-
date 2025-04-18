import time
import json
from pathlib import Path

SPAM_LIMIT = 4
SPAM_SECONDS = 10
BLOCK_DURATION = 60 * 30  # 30 минут

user_activity = {}
bans_file = Path("bans.json")

# Загружаем блокировки
def load_bans():
    if bans_file.exists():
        with open(bans_file, "r") as f:
            return json.load(f)
    return {}

# Сохраняем блокировки
def save_bans(data):
    with open(bans_file, "w") as f:
        json.dump(data, f)

user_blocked = load_bans()

def is_banned(user_id):
    now = time.time()
    uid = str(user_id)
    if uid in user_blocked:
        if now < user_blocked[uid]:
            return True
        else:
            del user_blocked[uid]
            save_bans(user_blocked)
    return False

def check_spam(user_id):
    now = time.time()
    uid = str(user_id)

    user_activity.setdefault(uid, [])
    user_activity[uid] = [t for t in user_activity[uid] if now - t <= SPAM_SECONDS]
    user_activity[uid].append(now)

    if len(user_activity[uid]) > SPAM_LIMIT:
        user_blocked[uid] = now + BLOCK_DURATION
        save_bans(user_blocked)
        return True
    return False
