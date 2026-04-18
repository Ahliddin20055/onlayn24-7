import os
import asyncio
import logging
import python_weather 
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

async def get_weather():
    try:
        async with python_weather.Client(unit=python_weather.METRIC) as weather_client:
            weather = await weather_client.get('Tashkent') 
            return f"{weather.temperature}°C"
    except:
        return "Noma'lum"

async def main():
    print("🚀 Bot ishga tushmoqda...")
    await client.start()
    Thread(target=run_flask).start()
    
    # Taymerlar
    status_timer = 0
    profile_timer = 3600 # 1 soatlik interval

    while True:
        try:
            # 1. ONLAYN HOLAT (Har 5 soniyada bir marta)
            if status_timer >= 5:
                await client(functions.account.UpdateStatusRequest(offline=False))
                status_timer = 0
            
            # 2. PROFIL YANGILASH (Har 3600 soniyada bir marta)
            if profile_timer >= 3600:
                uzb_iz = pytz.timezone('Asia/Tashkent')
                now = datetime.now(uzb_iz)
                vaqt = now.strftime("%H:%M")
                sana = now.strftime("%d.%m.%Y")
                kun = hafta_kunlari.get(now.strftime("%A"), "")
                havo = await get_weather()
                
                await client(functions.account.UpdateProfileRequest(
                    first_name=ismingiz,
                    last_name=f"| {vaqt} 🕒",
                    about=f"🌡 {havo} | 🕒 {vaqt} | 📅 {sana} | {kun} | 🟢"
                ))
                profile_timer = 0
            
            # Har 1 soniyada tsikl ishlaydi, hisoblagichlar oshib boradi
            status_timer += 1
            profile_timer += 1
            await asyncio.sleep(1) 
            
        except Exception as e:
            logging.error(f"Xatolik yuz berdi: {e}")
            await asyncio.sleep(5)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🔴 Bot to'xtatildi.")
