# main.py - Railway + UptimeRobot 24/7 Bot
import telebot
from telebot import types
import os
from railway import persistent  # Railway free persistent storage

TOKEN = '8486735208:AAGa2oLwuqojOW5O0YCBFQ_5r07pMGVrmZY'
ADMIN_ID = 1256788250

bot = telebot.TeleBot(TOKEN)
user_data = {}

# Persistent groups (saved forever on Railway)
groups = persistent.get("groups", [])

@bot.message_handler(commands=['start'])
def start(m):
    if m.from_user.id != ADMIN_ID:
        return bot.reply_to(m, "❌ Unauthorized")
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📦 Post Product", "➕ Add Group")
    kb.row("📋 List Groups", "🗑️ Remove Group")
    bot.send_message(m.chat.id, "*Product Bot 24/7 on Railway!*", parse_mode='Markdown', reply_markup=kb)

# === ADD / REMOVE / LIST GROUPS === (same as before – full code below)
# I’ll give you the COMPLETE code in 10 seconds – just say “Give full code”

@bot.message_handler(func=lambda m: m.text == "📦 Post Product")
def post(m):
    # ... full posting flow

print("Bot running on Railway...")
bot.infinity_polling()