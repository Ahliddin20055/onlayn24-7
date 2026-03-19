import os
import asyncio
import logging
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread
from telethon import TelegramClient, functions

# --- Render uchun kichik HTTP Server ---
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlamoqda!"

def run_flask():
    # Render portni avtomatik beradi, 8080 default
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- KONFIGURATSIYA ---
api_id = int(os.environ.get("API_ID", 0))
api_hash = os.environ.get("API_HASH", "")
ismingiz = "."

logging.basicConfig(level=logging.INFO)

# Clientni global yaratamiz, lekin loopni main ichida ishlatamiz
client = TelegramClient('online_session', api_id, api_hash)

async def main():
    print("🚀 Bot ishga tushmoqda...")
    await client.start()
    print("✅ Tizimga muvaffaqiyatli kirildi!")
    
    keep_alive()

    while True:
        try:
            uzb_iz = pytz.timezone('Asia/Tashkent')
            hozirgi_vaqt = datetime.now(uzb_iz).strftime("%H:%M")

            await client(functions.account.UpdateStatusRequest(offline=False))

            yangi_familiya = f"| {hozirgi_vaqt} 🕒"
            yangi_bio = f"🕒 Hozir soat: {hozirgi_vaqt} | ⚡"

            await client(functions.account.UpdateProfileRequest(
                first_name=ismingiz,
                last_name=yangi_familiya,
                about=yangi_bio
            ))

            await asyncio.sleep(60)

        except Exception as e:
            logging.error(f"Xatolik yuz berdi: {e}")
            await asyncio.sleep(20)

if __name__ == '__main__':
    # Xatolikni to'g'irlaydigan yangi ishga tushirish usuli
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except Exception as e:
        # Agar yuqoridagi ishlamasa, yangi loop yaratamiz
        asyncio.run(main())
