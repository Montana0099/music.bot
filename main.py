import os
import sqlite3
from telebot import TeleBot, types
from yt_dlp import YoutubeDL
from flask import Flask, request

# Bot tokenini shu yerga yozing
TOKEN = "8745750821:AAG4aUwkq4KaedaSBV9Tgtbbn20Az-51PDI"
bot = TeleBot(TOKEN)

app = Flask(__name__)

# --- MAʼLUMOTLAR BAZASI ---
def init_db():
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name):
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
    """, (user_id, username, first_name))
    conn.commit()
    conn.close()

init_db()

# --- MUSIQA QIDIRISH ---
def search_and_download_audio(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'music_downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            if 'entries' in info and len(info['entries']) > 0:
                video_info = info['entries'][0]
                filename = ydl.prepare_filename(video_info)
                return filename, video_info['title']
        except Exception as e:
            print(f"Yuklashda xatolik: {e}")
            return None, None

# --- BOT COMMANDLARI ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    bot.reply_to(message, f"Salom, {message.from_user.first_name}!\nMusiqa nomini yozing, men topaman. 🎵")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    query = message.text
    status_msg = bot.reply_to(message, "🔍 Qidirilmoqda...")
    
    if not os.path.exists('music_downloads'):
        os.makedirs('music_downloads')
        
    file_path, title = search_and_download_audio(query)
    
    if file_path and os.path.exists(file_path):
        bot.edit_message_text("📤 Yuborilmoqda...", chat_id=message.chat.id, message_id=status_msg.message_id)
        with open(file_path, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, caption=f"🎵 {title}")
        os.remove(file_path)
        bot.delete_message(message.chat.id, status_msg.message_id)
    else:
        bot.edit_message_text("❌ Hech narsa topilmadi.", chat_id=message.chat.id, message_id=status_msg.message_id)

# --- WEBHOOK VA SERVER QISMI ---
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    # RENDER_URL degan joyga Render bergan sayt manzilingizni qo'ying
    RENDER_URL = "https://music-bot-9nde.onrender.com" 
    bot.set_webhook(url=RENDER_URL + '/' + TOKEN)
    return "Bot faol!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
        
import os
import sqlite3
from telebot import TeleBot, types
from yt_dlp import YoutubeDL

# Bot tokenini shu yerga yozing yoki Render Env-dan oling
TOKEN = "8745750821:AAG4aUwkq4KaedaSBV9Tgtbbn20Az-51PDI"
bot = TeleBot(TOKEN)

# --- MAʼLUMOTLAR BAZASI BILAN ISHLASH ---
def init_db():
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    # Foydalanuvchilar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name):
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
    """, (user_id, username, first_name))
    conn.commit()
    conn.close()

# Bazani faollashtiramiz
init_db()

# --- MUSIQA QIDIRISH (YT-DLP) ---
def search_and_download_audio(query):
    # Yuklab olish sozlamalari
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'music_downloads/%(title)s.%(ext)s', # musiqalar shu papkaga tushadi
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }
    
    # YouTube-dan qidirish
    with YoutubeDL(ydl_opts) as ydl:
        try:
            # query orqali qidiruv beramiz (ytsearch:)
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            if 'entries' in info and len(info['entries']) > 0:
                video_info = info['entries'][0]
                # Yuklangan fayl nomini topamiz
                filename = ydl.prepare_filename(video_info)
                # Kengaytmasini mp3 ga o'zgartiramiz (chunki FFmpeg mp3 qiladi)
                mp3_filename = os.path.splitext(filename)[0] + ".mp3"
                return mp3_filename, video_info['title']
        except Exception as e:
            print(f"Xatolik yuz berdi: {e}")
            return None, None

# --- BOT BUYRUQLARI ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    # Foydalanuvchini bazaga qo'shamiz
    add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    
    welcome_text = f"Salom, {message.from_user.first_name}!\n\nMusiqa botga xush kelibsiz. Istalgan qoʻshiq nomi yoki ijrochini yozing, men uni topib beraman! 🎵"
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    query = message.text
    status_msg = bot.reply_to(message, "🔍 Qidirilmoqda, iltimos kuting...")
    
    # Papka borligini tekshiramiz
    if not os.path.exists('music_downloads'):
        os.makedirs('music_downloads')
        
    file_path, title = search_and_download_audio(query)
    
    if file_path and os.path.exists(file_path):
        bot.edit_message_text("📤 Musiqa yuklanmoqda...", chat_id=message.chat.id, message_id=status_msg.message_id)
        
        # Audio faylni yuboramiz
        with open(file_path, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, caption=f"🎵 {title}\n\n@SizningBotiz")
            
        # Yuklangan faylni o'chirib tashlaymiz (Xotira to'lib ketmasligi uchun)
        os.remove(file_path)
        bot.delete_message(message.chat.id, status_msg.message_id)
    else:
        bot.edit_message_text("❌ Afsuski, hech narsa topilmadi yoki yuklashda xatolik bo'ldi.", chat_id=message.chat.id, message_id=status_msg.message_id)

# Botni ishga tushirish (Web-hook kodingiz bo'lsa o'sha joyiga qo'ying)
if __name__ == "__main__":
    bot.delete_webhook()
    bot.infinity_polling()
# Botni ishga tushirish qismi
if __name__ == "__main__":
    # Avval faol bo'lgan webhookni o'chiramiz (shunda telefonda ishlaydi)
    bot.delete_webhook()
    
    print("Bot muvaffaqiyatli ishga tushdi...")
    bot.infinity_polling()
