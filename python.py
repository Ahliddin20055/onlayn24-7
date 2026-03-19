import os
import asyncio
import logging
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread
from telethon import TelegramClient, functions
from telethon.sessions import StringSession

# --- Render uchun HTTP Server ---
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlanyapti!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- KONFIGURATSIYA ---
# Bularni Render Environment Variables bo'limiga kiritishingiz shart!
api_id = int(os.environ.get("API_ID", 0))
api_hash = os.environ.get("API_HASH", "")
string_session = os.environ.get("STRING_SESSION", "")
ismingiz = "."

logging.basicConfig(level=logging.INFO)

# StringSession orqali client yaratish
client = TelegramClient(StringSession(string_session), api_id, api_hash)

async def main():
    print("🚀 Bot ishga tushmoqda...")
    await client.start()
    print("✅ Tizimga muvaffaqiyatli kirildi!")
    
    # Render o'chib qolmasligi uchun Flaskni ishga tushiramiz
    Thread(target=run_flask).start()

    while True:
        try:
            uzb_iz = pytz.timezone('Asia/Tashkent')
            hozirgi_vaqt = datetime.now(uzb_iz).strftime("%H:%M")
            
            # Onlayn holatni yangilash
            await client(functions.account.UpdateStatusRequest(offline=False))
            
            # Profilni yangilash (Qavslar to'g'irlandi)
            await client(functions.account.UpdateProfileRequest(
                first_name=ismingiz,
                last_name=f"| {hozirgi_vaqt} 🕒",
                about=f"🕒 Soat: {hozirgi_vaqt} | ⚡"
            ))
            
            await asyncio.sleep(15)
            
        except Exception as e:
            logging.error(f"Xatolik yuz berdi: {e}")
            await asyncio.sleep(20)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🔴 Bot to'xtatildi.")
