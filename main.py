import os
import telebot
from telebot import types
from flask import Flask, request

# 1
TOKEN = "8745750821:AAG4aUwkq4KaedaSBV9Tgtbbn20Az-51PDI"
bot = telebot.TeleBot(TOKEN)

# 2. Render uchun kichik veb-server yaratish
app = Flask(__name__)

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    return "Bot muvaffaqiyatli ishlamoqda!", 200

# 3. Botingizning asosiy funksiyalari (Sizning musiqangiz)
MENING_MUSIQAM = "CQACAgIAAxkBAANPakVFrq6-21UWylQp0X8TqI6oGlMAAlebAAKFQylK7ErzG8y-5bI8BA"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("🎵 Tasodifiy musiqa")
    item2 = types.KeyboardButton("📜 Janrlar")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, "Musiqa botga xush kelibsiz! \nTugmalardan birini tanlang:", reply_markup=markup)

@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    file_id = message.audio.file_id
    bot.reply_to(message, f"✅ Yangi musiqa ID kodi:\n\n`{file_id}`", parse_mode="Markdown")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "🎵 Tasodifiy musiqa":
        bot.send_message(message.chat.id, "Musiqa yuklanyapti... ⏳")
        bot.send_audio(message.chat.id, MENING_MUSIQAM, caption="Siz so'ragan ajoyib musiqa! 🔥")
    elif message.text == "📜 Janrlar":
        inline_markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Pop 🕺", callback_data="genre_pop")
        btn2 = types.InlineKeyboardButton("Rap 🎤", callback_data="genre_rap")
        inline_markup.add(btn1, btn2)
        bot.send_message(message.chat.id, "Janrni tanlang:", reply_markup=inline_markup)
    else:
        if "sher" in message.text.lower() or "musiqa" in message.text.lower(): 
            bot.send_message(message.chat.id, f"🔍 '{message.text}' bo'yicha musiqa topildi!")
            bot.send_audio(message.chat.id, MENING_MUSIQAM)
        else:
            bot.send_message(message.chat.id, f"😔 Kechirasiz, '{message.text}' bo'yicha hech narsa topilmadi.")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "genre_pop":
        bot.send_audio(call.message.chat.id, MENING_MUSIQAM, caption="Pop janridagi sara musiqa!")
    elif call.data == "genre_rap":
        bot.send_message(call.message.chat.id, "Tez orada Rap musiqalar qo'shiladi!")
    bot.answer_callback_query(call.id)

# 4. Serverni ishga tushirish qismi
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
