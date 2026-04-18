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
api_id = int(os.environ.get("API_ID", 0))
api_hash = os.environ.get("API_HASH", "")
string_session = os.environ.get("STRING_SESSION", "")

# Hafta kunlari lug'ati
hafta_kunlari = {
    "Monday": "Dushanba", "Tuesday": "Seshanba", "Wednesday": "Chorshanba",
    "Thursday": "Payshanba", "Friday": "Juma", "Saturday": "Shanba", "Sunday": "Yakshanba"
}

logging.basicConfig(level=logging.INFO)

client = TelegramClient(StringSession(string_session), api_id, api_hash)

async def update_status():
    """Onlayn holatni har 15 soniyada yangilab turadi"""
    while True:
        try:
            await client(functions.account.UpdateStatusRequest(offline=False))
            await asyncio.sleep(15)
        except Exception as e:
            logging.error(f"Status yangilashda xatolik: {e}")
            await asyncio.sleep(10)

async def update_profile():
    """Profil ismini va bio'ni har daqiqada yangilaydi"""
    while True:
        try:
            uzb_iz = pytz.timezone('Asia/Tashkent')
            now = datetime.now(uzb_iz)
            vaqt = now.strftime("%H:%M")
            sana = now.strftime("%d.%m.%Y")
            kun = hafta_kunlari.get(now.strftime("%A"), "")
            
            await client(functions.account.UpdateProfileRequest(
                first_name="Safarov Ahliddin",
                last_name=f"| {vaqt} 🕒",
                about=f"🕒 Vaqt: {vaqt} | 📅 {sana} | {kun} | 🟢"
            ))
            await asyncio.sleep(60)
        except Exception as e:
            logging.error(f"Profil yangilashda xatolik: {e}")
            await asyncio.sleep(60)

async def main():
    print("🚀 Bot ishga tushmoqda...")
    await client.start()
    print("✅ Tizimga muvaffaqiyatli kirildi!")
    
    # Flask serverini fon rejimida ishga tushirish
    Thread(target=run_flask).start()

    # Ikkala vazifani parallel ravishda ishga tushirish
    await asyncio.gather(update_status(), update_profile())

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🔴 Bot to'xtatildi.")
