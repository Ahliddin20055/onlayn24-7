import os
import asyncio
import logging
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread
from telethon import TelegramClient, functions
from telethon.sessions import StringSession
from PIL import Image, ImageDraw, ImageFont

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

# Hafta kunlari lug'ati
hafta_kunlari = {
    "Monday": "Dushanba", "Tuesday": "Seshanba", "Wednesday": "Chorshanba",
    "Thursday": "Payshanba", "Friday": "Juma", "Saturday": "Shanba", "Sunday": "Yakshanba"
}

logging.basicConfig(level=logging.INFO)
client = TelegramClient(StringSession(string_session), api_id, api_hash)

def create_image(text):
    # 500x500 o'lchamda qora rasm yaratish (o'rniga rasm faylini ochsangiz ham bo'ladi)
    img = Image.new('RGB', (500, 500), color=(0, 0, 0))
    d = ImageDraw.Draw(img)
    
    # Shriftni yuklash (agar .ttf faylingiz bo'lsa yo'lini ko'rsating, bo'lmasa default ishlatiladi)
    try:
        fnt = ImageFont.truetype("arial.ttf", 100)
    except:
        fnt = ImageFont.load_default()

    # Matnni markazga joylashtirish
    w, h = d.textsize(text, font=fnt) if hasattr(d, 'textsize') else (200, 100)
    d.text(((500-w)/2, (500-h)/2), text, font=fnt, fill=(255, 255, 255))
    
    img.save("photo.jpg")

async def main():
    print("🚀 Bot ishga tushmoqda...")
    await client.start()
    print("✅ Tizimga muvaffaqiyatli kirildi!")
    
    Thread(target=run_flask).start()

    while True:
        try:
            uzb_iz = pytz.timezone('Asia/Tashkent')
            now = datetime.now(uzb_iz)
            
            vaqt = now.strftime("%H:%M")
            sana = now.strftime("%d.%m.%Y")
            kun = hafta_kunlari.get(now.strftime("%A"), "")
            
            # 1. Rasm yaratish
            create_image(vaqt)
            
            # 2. Onlayn holatni yangilash
            await client(functions.account.UpdateStatusRequest(offline=False))
            
            # 3. Profil rasmini o'zgartirish
            file = await client.upload_file("photo.jpg")
            await client(functions.photos.UploadProfilePhotoRequest(file=file))
            
            # 4. Eski rasmlarni o'chirish (profil to'lib ketmasligi uchun)
            photos = await client.get_versions(functions.photos.GetUserPhotosRequest(
                user_id='me', offset=1, max_id=0, limit=1
            ))
            if photos.photos:
                await client(functions.photos.DeletePhotosRequest(id=[photos.photos[0]]))

            # 5. Profil ma'lumotlarini yangilash
            await client(functions.account.UpdateProfileRequest(
                first_name=ismingiz,
                last_name=f"| {vaqt} 🕒",
                about=f"🕒 Vaqt: {vaqt} | 📅 {sana} | {kun} | ⚡"
            ))
            
            await asyncio.sleep(60) # Rasmli soat uchun 60 soniya tavsiya etiladi
            
        except Exception as e:
            logging.error(f"Xatolik yuz berdi: {e}")
            await asyncio.sleep(20)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🔴 Bot to'xtatildi.")
