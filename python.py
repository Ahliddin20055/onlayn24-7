import os
import asyncio
import logging
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
            logging.info("Onlayn maqomi yangilandi. Status: OK")
            await asyncio.sleep(5)  # Har 5 soniyada onlaynlikni yangilash
        except Exception as e:
            logging.error(f"Onlaynlikda xatolik: {e}")
            await asyncio.sleep(10)

async def main():
    print("🚀 Bot ishga tushmoqda...")
    await client.start()
    print("✅ Tizimga muvaffaqiyatli kirildi!")
    
    # Render o'chib qolmasligi uchun Flaskni ishga tushiramiz
    Thread(target=run_flask).start()

    # Faqat onlayn ushlash vazifasini ishga tushiramiz
    await keep_online()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🔴 Bot to'xtatildi.")
