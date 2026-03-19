import os
from telethon import TelegramClient, functions
import asyncio
import logging
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread

# --- Render uchun kichik HTTP Server (UptimeRobot uchun) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlamoqda!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- KONFIGURATSIYA (Render/Environment Variables orqali) ---
# Bularni kodga yozmang, Render saytida 'Environment Variables' bo'limiga kiriting
api_id = int(os.environ.get("API_ID", 12345)) 
api_hash = os.environ.get("API_HASH", "Sizning_Hash_Bu_Yerda")
session_string = os.environ.get("SESSION_STRING") # String session xavfsizroq

ismingiz = "."

logging.basicConfig(level=logging.INFO)

# Agar session_string bo'lsa shundan, yo'q bo'lsa fayldan foydalanadi
if session_string:
    from telethon.sessions import StringSession
    client = TelegramClient(StringSession(session_string), api_id, api_hash)
else:
    client = TelegramClient('online_session', api_id, api_hash)

async def main():
    print("🚀 Bot ishga tushmoqda...")
    await client.start()
    print("✅ Tizimga muvaffaqiyatli kirildi!")
    
    # Render o'chib qolmasligi uchun serverni yoqamiz
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

            # Telegram limitlari uchun 60 soniya tavsiya etiladi (xavfsizroq)
            await asyncio.sleep(60)

        except Exception as e:
            logging.error(f"Xatolik yuz berdi: {e}")
            await asyncio.sleep(20)

if __name__ == '__main__':
    try:
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("🔴 Bot to'xtatildi.")
