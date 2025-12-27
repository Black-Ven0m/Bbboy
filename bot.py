import os
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types

# ====== BASIC CONFIG ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
GOD_ID = 5217960660  # <<< YAHAN APNA TELEGRAM NUMERIC ID DALO

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# ====== DATABASE SETUP ======
db = sqlite3.connect("venom.db")
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS members (
    telegram_id INTEGER PRIMARY KEY,
    username TEXT,
    role TEXT,
    level TEXT,
    join_date TEXT,
    status TEXT
)
""")
db.commit()

# ====== HELPERS ======
def get_member(uid):
    cur.execute("SELECT * FROM members WHERE telegram_id=?", (uid,))
    return cur.fetchone()

def is_god(uid):
    return uid == GOD_ID

def is_admin_or_god(uid):
    m = get_member(uid)
    return is_god(uid) or (m and m[2] == "ADMIN")

# ====== COMMANDS ======

@dp.message_handler(commands=["whoami"])
async def whoami(msg: types.Message):
    m = get_member(msg.from_user.id)
    if not m:
        return
    await msg.reply(f"""
<b>BLACK VENOM ACCESS</b>

USER  : {m[1]}
ROLE  : {m[2]}
LEVEL : {m[3]}
STATUS: {m[5]}
""")

@dp.message_handler(commands=["id"])
async def show_id(msg: types.Message):
    m = get_member(msg.from_user.id)
    if not m:
        return

    _, username, role, level, join_date, status = m
    tag = "∆VNM▲GØD" if role == "VNM GOD" else "∆VNM404"

    text = f"""
╔════════════════════════════╗
║     BLACK VENOM ID CARD    ║
╚════════════════════════════╝

NAME    : {username}
ROLE    : {role}
TAG     : {tag}
LEVEL   : {level}
JOINED  : {join_date}
STATUS  : {status}

ACCESS  : AUTHORIZED
"""
    await msg.reply(text)

@dp.message_handler(commands=["add"])
async def add_member(msg: types.Message):
    if not is_god(msg.from_user.id):
        return

    if not msg.reply_to_message:
        await msg.reply("Reply to a user with:\n/add ROLE LEVEL")
        return

    try:
        role, level = msg.get_args().split()
        user = msg.reply_to_message.from_user

        cur.execute("""
        INSERT OR REPLACE INTO members
        (telegram_id, username, role, level, join_date, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user.id,
            user.username or user.full_name,
            role,
            level,
            datetime.now().strftime("%d-%m-%Y"),
            "ACTIVE"
        ))
        db.commit()
        await msg.reply("✔ MEMBER ADDED")
    except:
        await msg.reply("Usage: reply + /add ROLE LEVEL")

@dp.message_handler(commands=["remove"])
async def remove_member(msg: types.Message):
    if not is_god(msg.from_user.id):
        return

    if not msg.reply_to_message:
        await msg.reply("Reply to a user with /remove")
        return

    user = msg.reply_to_message.from_user
    cur.execute("DELETE FROM members WHERE telegram_id=?", (user.id,))
    db.commit()
    await msg.reply("✖ MEMBER REMOVED")

@dp.message_handler(commands=["update"])
async def update_member(msg: types.Message):
    if not is_admin_or_god(msg.from_user.id):
        return

    if not msg.reply_to_message:
        await msg.reply("Reply to a user with:\n/update ROLE LEVEL")
        return

    try:
        role, level = msg.get_args().split()
        user = msg.reply_to_message.from_user
        cur.execute("""
        UPDATE members SET role=?, level=? WHERE telegram_id=?
        """, (role, level, user.id))
        db.commit()
        await msg.reply("✔ MEMBER UPDATED")
    except:
        await msg.reply("Usage: reply + /update ROLE LEVEL")

@dp.message_handler(commands=["list"])
async def list_members(msg: types.Message):
    if not is_admin_or_god(msg.from_user.id):
        return

    cur.execute("SELECT username, role, level, status FROM members")
    rows = cur.fetchall()
    if not rows:
        await msg.reply("No members found.")
        return

    text = "<b>BLACK VENOM MEMBERS</b>\n\n"
    for u, r, l, s in rows:
        text += f"• {u} | {r} | Lvl {l} | {s}\n"

    await msg.reply(text)

# ====== START ======
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
