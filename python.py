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
    return "✅ Bot muvaffaqiyatli ishlamoqda!"

def run_flask():
    # Render uchun 10000 porti ma'qulroq
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- KONFIGURATSIYA ---
api_id = int(os.environ.get("API_ID", 0))
api_hash = os.environ.get("API_HASH", "")
string_session = os.environ.get("STRING_SESSION", "")
ismingiz = "Safarov Ahliddin"

# Hafta kunlarini o'zbekchaga o'giramiz
hafta_kunlari = {
    "Monday": "Dushanba",
    "Tuesday": "Seshanba",
    "Wednesday": "Chorshanba",
    "Thursday": "Payshanba",
    "Friday": "Juma",
    "Saturday": "Shanba",
    "Sunday": "Yakshanba"
}

logging.basicConfig(level=logging.INFO)
client = TelegramClient(StringSession(string_session), api_id, api_hash)

async def main():
    print("🚀 Bot ishga tushmoqda...")
    await client.start()
    print("✅ Tizimga muvaffaqiyatli kirildi!")
    
    # Flaskni alohida thread-da ishga tushirish
    Thread(target=run_flask, daemon=True).start()

    while True:
        try:
            uzb_iz = pytz.timezone('Asia/Tashkent')
            now = datetime.now(uzb_iz)
            
            # Formatlash: 16:45, 19.03.2026, Payshanba
            hozirgi_vaqt = now.strftime("%H:%M")
            sana = now.strftime("%d.%m.%Y")
            hafta_kuni = hafta_kunlari[now.strftime("%A")]
            
            # Onlayn holatni yangilash
            await client(functions.account.UpdateStatusRequest(offline=False))
            
            # Profilni yangilash: Ism | Vaqt, About: Sana va Hafta kuni
            await client(functions.account.UpdateProfileRequest(
                first_name=f"{ismingiz}",
                last_name=f"| {hozirgi_vaqt} 🕒",
                about=f"📅 {sana} | {hafta_kuni} | ⚡ @Ahliddin_Safarov"
            ))
            
            # Telegram Flood limit (blok) olmaslik uchun 45-60 soniya tavsiya etiladi
            await asyncio.sleep(45)
            
        except Exception as e:
            logging.error(f"Xatolik yuz berdi: {e}")
            await asyncio.sleep(20)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🔴 Bot to'xtatildi.")
