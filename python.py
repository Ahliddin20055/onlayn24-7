import os
import asyncio
import logging
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread
from telethon import TelegramClient, functions, events
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

AUTO_REPLY_TEXT = "Xabaringizni qabul qildim ✅️ @Ahliddin_Safarov sizga tez orada javob yozadi 📝"

# Foydalanuvchilarning oxirgi javob olgan vaqtini saqlash uchun lug'at
user_last_replied = {}
COOLDOWN_MINUTES = 5  # Har necha daqiqada qayta javob berishi (daqiqalarda)

@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    if event.is_private:
        sender = await event.get_sender()
        if sender and not sender.is_self:
            user_id = sender.id
            now = datetime.now()

            # Tekshiramiz: foydalanuvchiga avval javob berilganmi va vaqt o'tdimi
            if user_id in user_last_replied:
                last_time = user_last_replied[user_id]
                if now - last_time < timedelta(minutes=COOLDOWN_MINUTES):
                    # Vaqt hali to'lmadi, qayta javob yuborilmaydi
                    return

            try:
                await event.reply(AUTO_REPLY_TEXT)
                user_last_replied[user_id] = now  # Oxirgi javob vaqtini yangilaymiz
                logging.info(f"Avto-javob yuborildi: {user_id}")
            except Exception as e:
                logging.error(f"Avto-javob yuborishda xatolik: {e}")

# 1. DOIMIY ONLAYN USHLASH FUNKSIYASI
async def keep_online():
    while True:
        try:
            await client(functions.account.UpdateStatusRequest(offline=False))
            await client.get_me()
            logging.info("Onlayn maqomi yangilandi. Status: OK")
            await asyncio.sleep(5)
        except Exception as e:
            logging.error(f"Onlaynlikda xatolik: {e}")
            await asyncio.sleep(10)

async def main():
    print("🚀 Bot ishga tushmoqda...")
    await client.start()
    print("✅ Tizimga muvaffaqiyatli kirildi!")
    
    Thread(target=run_flask).start()

    await asyncio.gather(
        keep_online(),
        client.run_until_disconnected()
    )

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🔴 Bot to'xtatildi.")
