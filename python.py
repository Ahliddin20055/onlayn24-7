import os
import asyncio
import logging
from datetime import datetime
import pytz
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
ismingiz = "Safarov Ahliddin"

# Tasdiqlanganlar ro'yxati (Bot har safar yonganda yangidan hisoblaydi)
allowed_users = set()

# Hafta kunlari lug'ati
hafta_kunlari = {
    "Monday": "Dushanba", "Tuesday": "Seshanba", "Wednesday": "Chorshanba",
    "Thursday": "Payshanba", "Friday": "Juma", "Saturday": "Shanba", "Sunday": "Yakshanba"
}

logging.basicConfig(level=logging.INFO)

# StringSession orqali client yaratish
client = TelegramClient(StringSession(string_session), api_id, api_hash)

# --- 1. SOAT VA PROFIL YANGILASH (O'zgartirilmadi) ---
async def clock_worker():
    while True:
        try:
            uzb_iz = pytz.timezone('Asia/Tashkent')
            now = datetime.now(uzb_iz)
            vaqt = now.strftime("%H:%M")
            sana = now.strftime("%d.%m.%Y")
            kun = hafta_kunlari.get(now.strftime("%A"), "")
            
            await client(functions.account.UpdateStatusRequest(offline=False))
            await client(functions.account.UpdateProfileRequest(
                first_name=ismingiz,
                last_name=f"| {vaqt} 🕒",
                about=f"🕒 {vaqt} | 📅 {sana} | {kun} | 🛡️ PM Guard Active ⚡️"
            ))
            await asyncio.sleep(40)
        except Exception as e:
            logging.error(f"Profil yangilashda xato: {e}")
            await asyncio.sleep(20)

# --- 2. AQLLI PM GUARD (QAT'IY VARIANT) ---
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def pm_guard(event):
    # Xabarni yuborgan foydalanuvchini olish
    sender = await event.get_sender()
    
    # O'zingizga o'zingiz yozsangiz yoki bot bo'lsa ishlamaydi
    if not sender or sender.bot or sender.self:
        return

    # Agar foydalanuvchi IDsi ruxsat berilganlar orasida bo'lmasa
    if sender.id not in allowed_users:
        try:
            # Xabarni o'qildi qilish (bot qayta-qayta javob bermasligi uchun)
            await client.send_read_acknowledge(event.chat_id)

            # 1. Ogohlantirish yuborish
            await event.reply(f"⚠️ **DIQQAT! SIZ TASDIQLANMAGANSIZ!**\n\n"
                              f"Assalomu alaykum, {sender.first_name}. "
                              f"Xavfsizlik yuzasidan xabar yozish imkoniyatingiz cheklandi. "
                              f"{ismingiz} sizni tasdiqlamagunlaricha blokda qolasiz.\n\n"
                              f"🕒 Iltimos, kuting...")
            
            # 2. Saved Messages'ga bildirishnoma
            await client.send_message('me', f"👤 **Yangi cheklangan foydalanuvchi:**\n"
                                            f"Ism: {sender.first_name}\n"
                                            f"User: @{sender.username}\n"
                                            f"ID: `{sender.id}`\n\n"
                                            f"Tasdiqlash: `.ok {sender.id}`")

            # 3. UNI QAT'IY BLOKLASH (Kontaktda bo'lsa ham)
            await client(functions.contacts.BlockRequest(id=sender.id))
            
        except Exception as e:
            logging.error(f"Himoya tizimi xatosi: {e}")

# --- 3. TASDIQLASH VA OCHISH ---
@client.on(events.NewMessage(outgoing=True, pattern=r'\.ok (\d+)'))
async def allow_user(event):
    user_id = int(event.pattern_match.group(1))
    
    try:
        # Blokdan chiqarish
        await client(functions.contacts.UnblockRequest(id=user_id))
        allowed_users.add(user_id)
        
        # Lichkasiga tabrik xabari
        await client.send_message(user_id, "✅ **Siz tasdiqlandingiz!**\nEndi menga bemalol xabar yuborishingiz mumkin.")
        
        await event.edit(f"✅ ID: {user_id} blokdan ochildi va tasdiqlandi!")
    except Exception as e:
        await event.edit(f"❌ Xatolik: {e}")

# --- 4. ISHGA TUSHIRISH ---
async def start_bot():
    print("🚀 Bot ishga tushmoqda...")
    await client.start()
    print("✅ Tizimga muvaffaqiyatli kirildi!")
    
    # Render uchun Flaskni alohida thread'da yoqamiz
    Thread(target=run_flask, daemon=True).start()

    # Soatni fonda boshlaymiz
    asyncio.create_task(clock_worker())
    
    # Xabarlarni kutish
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        print("🔴 Bot to'xtatildi.")
