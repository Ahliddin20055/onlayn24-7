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
ismingiz = "Safarov Ahliddin"

hafta_kunlari = {
    "Monday": "Dushanba", "Tuesday": "Seshanba", "Wednesday": "Chorshanba",
    "Thursday": "Payshanba", "Friday": "Juma", "Saturday": "Shanba", "Sunday": "Yakshanba"
}

logging.basicConfig(level=logging.INFO)

client = TelegramClient(StringSession(string_session), api_id, api_hash)

# 1. DOIMIY ONLAYN USHLASH FUNKSIYASI
async def keep_online():
    while True:
        try:
            # Telegramga "men hozirgina ilovani ochdim" degan signal yuboradi
            await client(functions.account.UpdateStatusRequest(offline=False))
            # Server bilan aloqani faol ushlash uchun yengil ping
            await client.get_me()
            await asyncio.sleep(5)  # Har 5 soniyada onlaynlikni yangilash
        except Exception as e:
            logging.error(f"Onlaynlikda xatolik: {e}")
            await asyncio.sleep(10)

# 2. PROFIL VA VAQTNI YANGILASH FUNKSIYASI
async def update_profile_loop():
    oxirgi_daqiqa = ""
    while True:
        try:
            uzb_iz = pytz.timezone('Asia/Tashkent')
            now = datetime.now(uzb_iz)
            joriy_daqiqa = now.strftime("%H:%M")

            # Profilni har soniyada emas, faqat daqiqa almashganda yangilaymiz (FloodWait oldini olish uchun)
            if joriy_daqiqa != oxirgi_daqiqa:
                sana = now.strftime("%d.%m.%Y")
                kun = hafta_kunlari.get(now.strftime("%A"), "")

                await client(functions.account.UpdateProfileRequest(
                    first_name=ismingiz,
                    last_name=f"| {joriy_daqiqa} 🕒",
                    about=f"🕒 Vaqt: {joriy_daqiqa} | 📅 {sana} | {kun} | 🟢"
                ))
                oxirgi_daqiqa = joriy_daqiqa
                logging.info(f"Profil yangilandi: {joriy_daqiqa}")
            
            await asyncio.sleep(15)  # Daqiqa almashishini tekshirish oralig'i
        except Exception as e:
            logging.error(f"Profil yangilashda xatolik: {e}")
            await asyncio.sleep(30)

async def main():
    print("🚀 Bot ishga tushmoqda...")
    await client.start()
    print("✅ Tizimga muvaffaqiyatli kirildi!")
    
    # Render o'chib qolmasligi uchun Flaskni ishga tushiramiz
    Thread(target=run_flask).start()

    # Ikkala vazifani ham parallel ravishda fonda ishga tushiramiz
    await asyncio.gather(
        keep_online(),
        update_profile_loop()
    )

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🔴 Bot to'xtatildi.")
