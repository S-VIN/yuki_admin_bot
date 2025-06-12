import os
import time
import logging

from telethon import TelegramClient
from telethon.tl.types import ChannelParticipantsRecent

from database import Database


# === CONFIG FROM ENVIRONMENT ===
API_ID = int(os.environ.get('API_ID', 000))
API_HASH = os.environ.get('API_HASH', '000')
CHANNEL_USERNAME = os.environ.get('CHANNEL_USERNAME', 'zlomysly')
ADMIN_USER_ID = os.environ.get('ADMIN_USER_ID')  # str or None
CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL', 300))

if not all([API_ID, API_HASH, CHANNEL_USERNAME]):
    raise ValueError("Missing required environment variables")


# Convert ADMIN_USER_ID if provided
if ADMIN_USER_ID:
    try:
        ADMIN_USER_ID = int(ADMIN_USER_ID)
    except ValueError:
        ADMIN_USER_ID = None


# === LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)


db = Database()
client = TelegramClient('data/bot', API_ID, API_HASH)


async def fetch_current_subscribers():
    users = {}
    async for user in client.iter_participants(CHANNEL_USERNAME, filter=ChannelParticipantsRecent()):
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        users[user.id] = {
            'username': user.username,
            'full_name': full_name
        }
    return users


async def send_update_message(text: str):
    target = ADMIN_USER_ID if ADMIN_USER_ID else 'me'
    await client.send_message(target, text)


async def check_subscribers():
    logging.info("Checking for subscriber updates...")
    current_subs = await fetch_current_subscribers()
    saved_subs = db.get_saved_subscribers()

    new_ids = set(current_subs.keys()) - set(saved_subs.keys())
    left_ids = set(saved_subs.keys()) - set(current_subs.keys())

    messages = []

    for user_id in new_ids:
        user = current_subs[user_id]
        messages.append(f"➕ New subscriber: {user['full_name']} (@{user['username'] or 'N/A'})")
        db.save_subscriber(user_id, user['username'], user['full_name'])

    for user_id in left_ids:
        user = saved_subs[user_id]
        messages.append(f"➖ Unsubscribed: {user['full_name']} (@{user['username'] or 'N/A'})")
        db.delete_subscriber(user_id)

    if messages:
        message = f"".join(messages)
        await send_update_message(message)
        logging.info("Update sent.")
    else:
        logging.info("No subscriber changes.")


async def main():
    await client.start()
    while True:
        try:
            await check_subscribers()
        except Exception as e:
            logging.exception("Error during subscriber check")
        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
