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

# Tasdiqlanganlar ro'yxati (Bot yonganda bo'sh bo'ladi)
allowed_users = set()

# Hafta kunlari lug'ati
hafta_kunlari = {
    "Monday": "Dushanba", "Tuesday": "Seshanba", "Wednesday": "Chorshanba",
    "Thursday": "Payshanba", "Friday": "Juma", "Saturday": "Shanba", "Sunday": "Yakshanba"
}

logging.basicConfig(level=logging.INFO)

# Client yaratish
client = TelegramClient(StringSession(string_session), api_id, api_hash)

# --- 1. SOAT VA PROFIL YANGILASH (24/7 ONLAYN) ---
async def clock_worker():
    while True:
        try:
            uzb_iz = pytz.timezone('Asia/Tashkent')
            now = datetime.now(uzb_iz)
            vaqt = now.strftime("%H:%M")
            sana = now.strftime("%d.%m.%Y")
            kun = hafta_kunlari.get(now.strftime("%A"), "")
            
            # Onlayn holatni saqlash
            await client(functions.account.UpdateStatusRequest(offline=False))
            
            # Profilni yangilash
            await client(functions.account.UpdateProfileRequest(
                first_name=ismingiz,
                last_name=f"| {vaqt} 🕒",
                about=f"🕒 {vaqt} | 📅 {sana} | {kun} | 🛡️ PM Guard Active 🌐"
            ))
            await asyncio.sleep(40)
        except Exception as e:
            logging.error(f"Soatda xato: {e}")
            await asyncio.sleep(20)

# --- 2. QAT'IY PM GUARD (HAMMANI BLOKLASH) ---
# Bu yerda func=lambda e: e.is_private qo'shildi, faqat lichkani ushlash uchun
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def pm_guard(event):
    # Kim yozganini aniqlaymiz
    sender = await event.get_sender()
    
    # O'zingiz yoki botlar bo'lsa, tegmaydi
    if not sender or sender.bot or sender.self:
        return

    # Agar u hali tasdiqlanmagan bo'lsa (ro'yxatda yo'q bo'lsa)
    if sender.id not in allowed_users:
        try:
            # 1. Xabarni darhol "O'qilgan" qilish
            await client.send_read_acknowledge(event.chat_id)

            # 2. Uni bloklash (Xabar yozish joyini yopish uchun birinchi bloklaymiz)
            await client(functions.contacts.BlockRequest(id=sender.id))

            # 3. Unga ogohlantirish yuborish (blokdan oldin yuborishga ulguradi)
            await event.reply(f"⚠️ **DIQQAT! SIZ TASDIQLANMAGANSIZ!**\n\n"
                              f"Assalomu alaykum, {sender.first_name}. "
                              f"Siz {ismingiz} tomonidan tasdiqlanmagansiz. "
                              f"Hozircha xabar yozish imkoniyatingiz cheklandi.\n\n"
                              f"🕒 Iltimos, tasdiqlashlarini kuting...")
            
            # 4. Sizga "Saved Messages"ga bildirishnoma yuborish
            await client.send_message('me', f"👤 **Yangi cheklangan foydalanuvchi:**\n"
                                            f"Ism: {sender.first_name}\n"
                                            f"ID: `{sender.id}`\n\n"
                                            f"Ruxsat berish: `.ok {sender.id}`")
            
        except Exception as e:
            logging.error(f"Himoya xatosi: {e}")

# --- 3. TASDIQLASH VA BLOKDAN OCHISH ---
@client.on(events.NewMessage(outgoing=True, pattern=r'\.ok (\d+)'))
async def allow_user(event):
    user_id = int(event.pattern_match.group(1))
    
    try:
        # Blokdan chiqarish
        await client(functions.contacts.UnblockRequest(id=user_id))
        
        # Ro'yxatga qo'shish
        allowed_users.add(user_id)
        
        # O'sha odamga xabar yuborish
        await client.send_message(user_id, "✅ **Siz tasdiqlandingiz!**\nEndi menga bemalol yozishingiz mumkin.")
        
        await event.edit(f"✅ ID: {user_id} blokdan chiqarildi va tasdiqlandi!")
    except Exception as e:
        await event.edit(f"❌ Xatolik: {e}")

# --- 4. ISHGA TUSHIRISH ---
async def start_bot():
    print("🚀 Bot 100% quvvat bilan ishga tushmoqda...")
    await client.start()
    print("✅ Tizimga kirildi!")
    
    # Render o'chib qolmasligi uchun Flask
    Thread(target=run_flask, daemon=True).start()

    # Soatni fonda yoqish
    asyncio.create_task(clock_worker())
    
    # Botni har doim onlayn va xabarda ushlash
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        # Xatolarni oldini oluvchi eng yangi ishga tushirish usuli
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        print("🔴 Bot to'xtatildi.")

