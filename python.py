import os
import asyncio
from telethon import TelegramClient, functions
from telethon.sessions import StringSession
from datetime import datetime
import pytz

# --- KONFIGURATSIYA ---
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
string_session = os.environ.get("STRING_SESSION")
ismingiz = "."

client = TelegramClient(StringSession(string_session), api_id, api_hash)

async def main():
    await client.start()
    print("✅ Bot muvaffaqiyatli ishga tushdi!")
    
    while True:
        try:
            uzb_iz = pytz.timezone('Asia/Tashkent')
            hozirgi_vaqt = datetime.now(uzb_iz).strftime("%H:%M")
            
            await client(functions.account.UpdateStatusRequest(offline=False))
            await client(functions.account.UpdateProfileRequest(
                first_name=ismingiz,
                last_name=f"| {hozirgi_vaqt} 🕒",
                about=f"🕒 Soat: {hozirgi_vaqt} | ⚡"
            )
            await asyncio.sleep(60)
        except Exception as e:
            print(f"Xatolik: {e}")
            await asyncio.sleep(20)

if __name__ == '__main__':
    asyncio.run(main())
