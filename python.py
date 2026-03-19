import os
import asyncio
import logging
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread
from telethon import TelegramClient, functions

# --- Render uchun HTTP Server ---
app = Flask('')
@app.route('/')
def home(): return "Bot ishlamoqda!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- KONFIGURATSIYA ---
api_id = int(os.environ.get("API_ID", 0))
api_hash = os.environ.get("API_HASH", "")
ismingiz = "."

logging.basicConfig(level=logging.INFO)

# DIQQAT: Fayl nomini GitHub-dagidek to'liq ko'rsatamiz
session_file = 'online_session.session'
client = TelegramClient('online_session', api_id, api_hash)

async def main():
    print("🚀 Bot ishga tushmoqda...")
    
    # Session fayli borligini tekshirish
    if os.path.exists(session_file):
        print(f"✅ {session_file} topildi, ulanish kutilmoqda...")
    else:
        print(f"❌ {session_file} topilmadi! Shuning uchun kod so'ralmoqda.")

    await client.connect()
    
    if not await client.is_user_authorized():
        print("⚠️ Avtorizatsiya talab qilinadi. Terminal interaktiv emas!")
        return # Bu yerda EOFError chiqishining oldini olamiz

    print("✅ Tizimga muvaffaqiyatli kirildi!")
    
    Thread(target=run_flask).start()

    while True:
        try:
            uzb_iz = pytz.timezone('Asia/Tashkent')
            hozirgi_vaqt = datetime.now(uzb_iz).strftime("%H:%M")
            await client(functions.account.UpdateStatusRequest(offline=False))
            
            await client(functions.account.UpdateProfileRequest(
                first_name=ismingiz,
                last_name=f"| {hozirgi_vaqt} 🕒",
                about=f"🕒 Hozir soat: {hozirgi_vaqt} | ⚡"
            ))
            await asyncio.sleep(60)
        except Exception as e:
            logging.error(f"Xatolik: {e}")
            await asyncio.sleep(20)

if __name__ == '__main__':
    asyncio.run(main())
