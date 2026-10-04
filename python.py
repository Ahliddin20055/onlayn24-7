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

# Hafta kunlari lug'ati (O'zbek tilida)
WEEKDAYS = {
    0: "Dushanba",
    1: "Seshanba",
    2: "Chorshanba",
    3: "Payshanba",
    4: "Juma",
    5: "Shanba",
    6: "Yakshanba"
}

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

# 2. PROFIL NOMI VA BIO'SINI YANGILASH FUNKSIYASI (SOAT, SANA, HAFTA KUNI)
async def update_profile_clock():
    last_minute = None
    while True:
        try:
            # O'zbekiston vaqti (UTC+5)
            tz = timedelta(hours=5)
            now = datetime.utcnow() + tz
            
            # Har daqiqada bir marta yangilaymiz
            current_minute = now.minute
            if current_minute != last_minute:
                last_minute = current_minute

                time_str = now.strftime("%H:%M")          # Masalan: 14:30
                date_str = now.strftime("%d.%m.%Y")       # Masalan: 25.10.2026
                weekday_str = WEEKDAYS[now.weekday()]     # Masalan: Dushanba

                # Profil ismi: Safarov Ahliddin | 14:30
                new_first_name = "Safarov Ahliddin"
                new_last_name = f"| {time_str} ⏰️"

                # Profil biosidagi matn
                new_bio = f"⏰ Vaqt: {time_str} | 📅 Sana: {date_str} | 🗓 {weekday_str}"

                # Ism va bio'ni update qilish
                await client(functions.account.UpdateProfileRequest(
                    first_name=new_first_name,
                    last_name=new_last_name,
                    about=new_bio
                ))
                logging.info(f"Profil yangilandi: {new_first_name} {new_last_name} — {new_bio}")

            await asyncio.sleep(30)  # Har 30 soniyada vaqtni tekshirib turadi
        except Exception as e:
            logging.error(f"Profilni yangilashda xatolik: {e}")
            await asyncio.sleep(60)

async def main():
    print("🚀 Bot ishga tushmoqda...")
    await client.start()
    print("✅ Tizimga muvaffaqiyatli kirildi!")
    
    Thread(target=run_flask).start()

    await asyncio.gather(
        keep_online(),
        update_profile_clock(),
        client.run_until_disconnected()
    )

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🔴 Bot to'xtatildi.")
