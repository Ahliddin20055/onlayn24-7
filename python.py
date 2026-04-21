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
    return "Botlar ishlayapti!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- KONFIGURATSIYA ---
# 1-akkaunt uchun
api_id_1 = int(os.environ.get("API_ID_1", 0))
api_hash_1 = os.environ.get("API_HASH_1", "")
session_1 = os.environ.get("STRING_SESSION_1", "")
name_1 = "Safarov Ahliddin" # 1-profil uchun ism

# 2-akkaunt uchun
api_id_2 = int(os.environ.get("API_ID_2", 0))
api_hash_2 = os.environ.get("API_HASH_2", "")
session_2 = os.environ.get("STRING_SESSION_2", "")
name_2 = "🥰🥰" # 2-profil uchun ism

hafta_kunlari = {
    "Monday": "Dushanba", "Tuesday": "Seshanba", "Wednesday": "Chorshanba",
    "Thursday": "Payshanba", "Friday": "Juma", "Saturday": "Shanba", "Sunday": "Yakshanba"
}

logging.basicConfig(level=logging.INFO)

async def update_status(client):
    while True:
        try:
            await client(functions.account.UpdateStatusRequest(offline=False))
            await asyncio.sleep(5)
        except Exception as e:
            logging.error(f"Status xatolik: {e}")
            await asyncio.sleep(10)

async def update_profile(client, first_name):
    while True:
        try:
            uzb_iz = pytz.timezone('Asia/Tashkent')
            now = datetime.now(uzb_iz)
            vaqt = now.strftime("%H:%M")
            sana = now.strftime("%d.%m.%Y")
            kun = hafta_kunlari.get(now.strftime("%A"), "")
            
            await client(functions.account.UpdateProfileRequest(
                first_name=first_name,
                last_name=f"| {vaqt} 🕒",
                about=f"🕒 Vaqt: {vaqt} | 📅 {sana} | {kun} | 🟢"
            ))
            await asyncio.sleep(60)
        except Exception as e:
            logging.error(f"Profil yangilash xatolik: {e}")
            await asyncio.sleep(60)

async def start_bot(api_id, api_hash, session, name):
    client = TelegramClient(StringSession(session), api_id, api_hash)
    await client.start()
    print(f"✅ {name} tizimga kirdi!")
    await asyncio.gather(update_status(client), update_profile(client, name))

async def main():
    print("🚀 Botlar ishga tushmoqda...")
    Thread(target=run_flask).start()
    
    # Ikkala akkauntni parallel ishga tushiramiz
    tasks = [
        start_bot(api_id_1, api_hash_1, session_1, name_1),
        start_bot(api_id_2, api_hash_2, session_2, name_2)
    ]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🔴 Botlar to'xtatildi.")
