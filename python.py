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

# Kimlarga ogohlantirish yuborilganini eslab qolish uchun (takrorlanmasligi uchun)
greeted_users = set()

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
                about=f"🕒 {vaqt} | 📅 {sana} | {kun} | 🟢 24/7 Online"
            ))
            await asyncio.sleep(40)
        except Exception as e:
            logging.error(f"Soatda xato: {e}")
            await asyncio.sleep(20)

# --- 2. AVTOMATIK TUSHUNTIRISH (BOT EFFEKTI) ---
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_greeting(event):
    sender = await event.get_sender()
    
    # O'zingiz yoki botlar bo'lsa, tegmaydi
    if not sender or sender.bot or sender.self:
        return

    # Agar bu odamga hali tushuntirish yuborilmagan bo'lsa
    if sender.id not in greeted_users:
        try:
            # Xabarni o'qildi qilish
            await client.send_read_acknowledge(event.chat_id)

            # SIZ AYTGAN KENG TUSHUNTIRISH MATNI
            intro_text = (
                f"👋 **Assalomu alaykum, {sender.first_name}!**\n\n"
                f"📢 **HURMATLI FOYDALANUVCHI!**\n\n"
                f"Meni juda zarur ishingiz bo'lmasa, iltimos, bezovta qilmang. "
                f"Vaqtim chegaralanganligi sababli barcha xabarlarga javob bera olmayman.\n\n"
                f"💡 **Eslatma:**\n"
                f"• Reklama yoki foydasiz suhbatlar uchun yozmang.\n"
                f"• Muhim masala bo'lsa, qisqa va lo'nda tushuntiring.\n"
                f"• Ismingiz va maqsadingizni aniq yozing.\n\n"
                f"Sizning xabaringiz qabul qilindi, agar kerak bo'lsa {ismingiz} o'zi siz bilan bog'lanadi. Rahmat!"
            )

            # Ogohlantirishni yuborish
            await event.reply(intro_text)
            
            # Ro'yxatga qo'shish (bot o'chib-yonmaguncha qayta yubormaydi)
            greeted_users.add(sender.id)
            
            # O'zingizga bildirishnoma
            await client.send_message('me', f"📩 **Yangi suhbatdosh:**\nIsm: {sender.first_name}\nID: `{sender.id}`")

        except Exception as e:
            logging.error(f"Greeting xatosi: {e}")

# --- 3. ISHGA TUSHIRISH ---
async def start_bot():
    print("🚀 Bot 24/7 va Auto-Intro bilan ishga tushmoqda...")
    await client.start()
    print("✅ Tizimga kirildi!")
    
    # Render o'chib qolmasligi uchun Flask
    Thread(target=run_flask, daemon=True).start()

    # Soatni fonda yoqish
    asyncio.create_task(clock_worker())
    
    # Botni doimiy eshitish rejimida ushlash
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        print("🔴 Bot to'xtatildi.")
