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

# --- ALLOHNING 99 TA ISMI MANBASI ---
NAMES_OF_ALLAH = [
    ("الله", "Allah", "Yagona Iloh"),
    ("الرَّحْمَنُ", "Ar-Rahmon", "O'ta mehribon"),
    ("الرَّحِيمُ", "Ar-Rahim", "Juda rahmli"),
    ("الْمَلِكُ", "Al-Malik", "Barcha narsaning podshohi"),
    ("الْقُدُّوسُ", "Al-Quddus", "Barcha ayblardan xoli"),
    ("السَّلاَمُ", "As-Salam", "Tinchlik va omonlik beruvchi"),
    ("الْمُؤْمِنُ", "Al-Mo'min", "Iymon va omonlik bag'ishlovchi"),
    ("الْمُهَيْمِنُ", "Al-Muhaymin", "Hamma narsani qamrab oluvchi va kuzatib turuvchi"),
    ("الْعَزِيزُ", "Al-Aziz", "Izzat va quvvat egasi"),
    ("الْجَبَّارُ", "Al-Jabbor", "O'z hukmini o'tkazuvchi"),
    ("الْمُتَكَبِّرُ", "Al-Mutakabbir", "Kattalik va buyuklik egasi"),
    ("الْخَالِقُ", "Al-Xoliq", "Yaratuvchi"),
    ("الْبَارِئُ", "Al-Bari'", "Yo'qdan bor qiluvchi"),
    ("الْمُصَوِّرُ", "Al-Musavvir", "Surat va shakl beruvchi"),
    ("الْغَفَّارُ", "Al-Ghaffor", "Ko'plab mag'firat qiluvchi"),
    ("الْقَهَّارُ", "Al-Qahhor", "Bo'ysundiruvchi va g'olib"),
    ("الْوَهَّابُ", "Al-Vahhob", "Behisob ne'matlar beruvchi"),
    ("الرَّزَّاقُ", "Ar-Razzoq", "Rizq beruvchi"),
    ("الْفَتَّاحُ", "Al-Fattoh", "Hukm qiluvchi va yo'l ochuvchi"),
    ("الْعَلِيمُ", "Al-Alim", "Hamma narsani biluvchi"),
    ("الْقَابِضُ", "Al-Qobiz", "Rizqni toraytiruvchi va jonlarni oluvchi"),
    ("الْبَاسِطُ", "Al-Basit", "Rizqni kengaytiruvchi va jon beruvchi"),
    ("الْخَافِضُ", "Al-Xofiz", "Darajalarni pasaytiruvchi"),
    ("الرَّافِعُ", "Ar-Rofi'", "Darajalarni ko'taruvchi"),
    ("الْمُعِزُّ", "Al-Mu'izz", "Aziz va mukarram qiluvchi"),
    ("الْمُذِلُّ", "Al-Muzill", "Xor qiluvchi"),
    ("السَّمِيعُ", "As-Sami'", "Har bir narsani eshituvchi"),
    ("الْبَصِيرُ", "Al-Basir", "Har bir narsani ko'rib turuvchi"),
    ("الْحَكَمُ", "Al-Hakam", "Haqiqiy Hakam va adolat qiluvchi"),
    ("الْعَدْلُ", "Al-Adl", "Juda adolatli"),
    ("اللَّطِيفُ", "Al-Latif", "Lutf qiluvchi va barcha nozikliklarni biluvchi"),
    ("الْخَبِيرُ", "Al-Xabir", "Hamma narsadan xabardor"),
    ("الْحَلِيمُ", "Al-Halim", "G'azab qilmaydigan, yumshoq muomala qiluvchi"),
    ("الْعَظِيمُ", "Al-Azim", "Buyuk va ulug'"),
    ("الْغَفُورُ", "Al-Ghafur", "Kechirimli va mag'firatli"),
    ("الشَّكُورُ", "Ash-Shakur", "Oz amalgayam ko'p mukofot beruvchi"),
    ("الْعَلِيُّ", "Al-Aliy", "Yuksak va oily"),
    ("الْكَبِيرُ", "Al-Kabir", "Juda buyuk"),
    ("الْحَفِيظُ", "Al-Hafiz", "Hamma narsani saqlovchi"),
    ("الْمُقِيتُ", "Al-Muqit", "Oziqlantiruvchi va quvvat beruvchi"),
    ("الْحَسِيبُ", "Al-Hasib", "Kifoya qiluvchi va hisob oluvchi"),
    ("الْجَلِيلُ", "Al-Jalil", "Ulug'lik va haybat egasi"),
    ("الْكَرِيمُ", "Al-Karim", "Saxovatli va saxiy"),
    ("الرَّقِيبُ", "Ar-Raqib", "Kuzatib va nazorat qilib turuvchi"),
    ("الْمُجِيبُ", "Al-Mujib", "Duolarni qabul qiluvchi"),
    ("الْوَاسِعُ", "Al-Vasi'", "Keng qamrovli va cheksiz"),
    ("الْحَكِيمُ", "Al-Hakim", "Hikmat egasi"),
    ("الْوَدُودُ", "Al-Vadud", "O'z bandalarini yaxshi ko'ruvchi"),
    ("الْمَجِيدُ", "Al-Majid", "Shon-sharaf va ulug'lik egasi"),
    ("الْبَاعِثُ", "Al-Ba'is", "Qayta tiriltiruvchi"),
    ("الشَّهِيدُ", "Ash-Shahid", "Har bir narsaga guvoh"),
    ("الْحَقُّ", "Al-Haqq", "Haqiqiy va o'zgarmas Iloh"),
    ("الْوَكِيلُ", "Al-Vakil", "Barcha ishlarni topshirishga loyiq vakil"),
    ("الْقَوِيُّ", "Al-Qaviy", "Juda kuchli va qudratli"),
    ("الْمَتِينُ", "Al-Matin", "Mustahkam va metin qudrat egasi"),
    ("الْوَلِيُّ", "Al-Valiy", "Do'st va yordamchi"),
    ("الْحَمِيدُ", "Al-Hamid", "Hamdu sanoga loyiq"),
    ("الْمُحْصِي", "Al-Muhsi", "Hamma narsaning hisobini biluvchi"),
    ("الْمُبْدِئُ", "Al-Mubdi'", "Ilk bor yo'qdan bor qilgan"),
    ("الْمُعِيدُ", "Al-Mu'id", "Vafotdan so'ng qayta tiriltiruvchi"),
    ("الْمُحْيِي", "Al-Muhyi", "Hayot beruvchi"),
    ("الْمُمِيتُ", "Al-Mumit", "O'lim beruvchi"),
    ("الْحَيُّ", "Al-Hayy", "Abadiy tirik"),
    ("الْقَيُّومُ", "Al-Qayyum", "O'z-o'zidan bor va barchani tutib turuvchi"),
    ("الْوَاجِدُ", "Al-Vojid", "Istalgan narsasini topuvchi"),
    ("الْمَاجِدُ", "Al-Mojid", "Oliy martabali va saxovatli"),
    ("الْوَاحِدُ", "Al-Vohid", "Yagona va yakka"),
    ("الصَّمَدُ", "As-Somad", "Hech kimga muhtoj bo'lmagan, barcha unga muhtoj"),
    ("الْقَادِرُ", "Al-Qodir", "Hamma narsaga qudrati yetuvchi"),
    ("الْمُقْتَدِرُ", "Al-Muqtadir", "Cheksiz qudrat egasi"),
    ("الْمُقَدِّمُ", "Al-Muqaddim", "Oldinga suruvchi"),
    ("الْمُؤَخِّرُ", "Al-Muaxxir", "Orqaga suruvchi"),
    ("الأَوَّلُ", "Al-Avval", "Boshi bo'lmagan birinchi"),
    ("الأخِرُ", "Al-Axir", "Oxiri bo'lmagan abadiy"),
    ("الظَّاهِرُ", "Az-Zohir", "Ochiq-oydin va belgilari bor"),
    ("الْبَاطِنُ", "Al-Botin", "Yashirin va ko'zga ko'rinmas"),
    ("الْوَالِي", "Al-Vali", "Barcha narsaning hukmdori"),
    ("الْمُتَعَالِي", "Al-Muta'ali", "Har qanday aybdan yuksak"),
    ("الْبَرُّ", "Al-Barr", "Yaxshilik va ehson egasi"),
    ("التَّوَّابُ", "At-Tavvob", "Tavbalarni qabul qiluvchi"),
    ("الْمُنْتَقِمُ", "Al-Muntaqim", "Zolimlardan intiqom oluvchi"),
    ("العَفُوُّ", "Al-Afuvv", "Kechiruvchi va afv etuvchi"),
    ("الرَّؤُوفُ", "Ar-Ra'uf", "Juda mehribon va shafqatli"),
    ("مَالِكُ الْمُلْكِ", "Malikul-Mulk", "Mulkning haqiqiy egasi"),
    ("ذُو الْجَلاَلِ وَالإِكْرَامِ", "Zul-Jalali val-Ikrom", "Ulug'lik va ikrom egasi"),
    ("الْمُقْسِطُ", "Al-Muqsit", "Adolat qiluvchi"),
    ("الْجَامِعُ", "Al-Jami'", "Odamlarni jamlovchi"),
    ("الْغَنِيُّ", "Al-Ghaniy", "Boy va hech kimga muhtoj emas"),
    ("الْمُغْنِي", "Al-Mughni", "Boyituvchi va bezatuvchi"),
    ("الْمَانِعُ", "Al-Mani'", "Man etuvchi va to'suvchi"),
    ("الضَّارُّ", "Az-Zorr", "Zarar yetkazuvchi (sinov uchun)"),
    ("النَّافِعُ", "An-Nafi'", "Foyda beruvchi"),
    ("النُّورُ", "An-Nur", "Nurlar nuri va yo'l ko'rsatuvchi"),
    ("الْهَادِي", "Al-Hadi", "To'g'ri yo'lga boshlovchi"),
    ("الْبَدِيعُ", "Al-Badi'", "Yo'qdan mislsiz qilib yaratuvchi"),
    ("الْبَاقِي", "Al-Baqi", "Mangu va abadiy bo'lgan"),
    ("الْوَارِثُ", "Al-Varis", "Barcha narsaning chinakam vorisi"),
    ("الرَّشِيدُ", "Ar-Rashid", "To'g'ri yo'l ko'rsatuvchi Hakam"),
    ("الصَّبُورُ", "As-Sabur", "Juda sabrli")
]

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

# 2. HAR KUNI BIONU ALASHTIRISH FUNKSIYASI
async def auto_change_bio():
    while True:
        try:
            # Yilning nechanchi kuni ekanligiga qarab ismni tanlaydi (1-365 kunga mos holda)
            day_of_year = asyncio.get_event_loop().time()
            # Kunlik indeks hosil qilish (0 dan 98 gacha aylanadi)
            import time
            current_day = int(time.time() // 86400)
            name_index = current_day % len(NAMES_OF_ALLAH)
            
            arabic, transliteration, meaning = NAMES_OF_ALLAH[name_index]
            
            # Formati: Arabcha Uzbekcha (Tarjimasi)
            new_bio = f"{arabic} {transliteration} ({meaning})"
            
            # Bio uzunligini tekshirish (Telegram biosi ko'pi bilan 70 belgi bo'lishi kerak)
            if len(new_bio) > 70:
                new_bio = new_bio[:70]

            await client(functions.account.UpdateProfileRequest(about=new_bio))
            logging.info(f"Bio muvaffaqiyatli yangilandi: {new_bio}")
            
            # Har 1 soatda bio to'g'ri turganini tekshirib/yangilab turadi
            await asyncio.sleep(3600)
        except Exception as e:
            logging.error(f"Bioni yangilashda xatolik: {e}")
            await asyncio.sleep(60)

async def main():
    print("🚀 Bot ishga tushmoqda...")
    await client.start()
    print("✅ Tizimga muvaffaqiyatli kirildi!")
    
    # Render o'chib qolmasligi uchun Flaskni ishga tushiramiz
    Thread(target=run_flask).start()

    # Ham onlayn ushlash, ham Bioni yangilash vazifalarini birga ishga tushiramiz
    await asyncio.gather(
        keep_online(),
        auto_change_bio()
    )

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🔴 Bot to'xtatildi.")
