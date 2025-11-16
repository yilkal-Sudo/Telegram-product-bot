# bot.py
import telebot
from telebot import types
import json
import os

TOKEN = '8486735208:AAGa2oLwuqojOW5O0YCBFQ_5r07pMGVrmZY'
ADMIN_ID = 1256788250
DATA_FILE = '/data/groups.json'  # Render persistent storage

bot = telebot.TeleBot(TOKEN)

def load_groups():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_groups(groups):
    os.makedirs('/data', exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(groups, f)

groups = load_groups()
user_data = {}

@bot.message_handler(commands=['start'])
def start(m):
    if m.from_user.id != ADMIN_ID: return bot.reply_to(m, "Unauthorized")
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Post Product", "Add Group", "List Groups")
    bot.send_message(m.chat.id, "*Bot Ready!*", parse_mode='Markdown', reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == "Add Group")
def add_g(m):
    if m.from_user.id != ADMIN_ID: return
    msg = bot.send_message(m.chat.id, "Send *@username* (bot must be admin):")
    bot.register_next_step_handler(msg, save_g)

def save_g(m):
    if m.from_user.id != ADMIN_ID: return
    if not m.text.startswith('@'): return bot.reply_to(m, "Send @username")
    try:
        chat = bot.get_chat(m.text)
        gid = str(chat.id)
        if gid not in groups:
            groups.append(gid)
            save_groups(groups)
            bot.reply_to(m, f"Added {m.text}")
        else:
            bot.reply_to(m, "Already added")
    except:
        bot.reply_to(m, "Bot not admin there")

@bot.message_handler(func=lambda m: m.text == "List Groups")
def list_g(m):
    if m.from_user.id != ADMIN_ID: return
    if not groups:
        return bot.reply_to(m, "No groups")
    txt = "*Groups:*\n"
    for g in groups:
        try:
            c = bot.get_chat(g)
            txt += f"• {c.title}\n"
        except:
            txt += f"• {g}\n"
    bot.send_message(m.chat.id, txt, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "Post Product")
def post(m):
    if m.from_user.id != ADMIN_ID: return
    if not groups: return bot.reply_to(m, "Add group first")
    user_data[m.from_user.id] = {}
    bot.send_message(m.chat.id, "Send *image URL or photo*")
    bot.register_next_step_handler(m, get_img)

def get_img(m):
    uid = m.from_user.id
    if m.photo:
        user_data[uid]['img'] = m.photo[-1].file_id
    elif m.text and m.text.startswith('http'):
        user_data[uid]['img'] = m.text
    else:
        return bot.reply_to(m, "Invalid image")
    bot.send_message(m.chat.id, "*Name*:")
    bot.register_next_step_handler(m, get_name)

def get_name(m):
    user_data[m.from_user.id]['name'] = m.text
    bot.send_message(m.chat.id, "*Price*:")
    bot.register_next_step_handler(m, get_price)

def get_price(m):
    user_data[m.from_user.id]['price'] = m.text
    bot.send_message(m.chat.id, "*Description*:")
    bot.register_next_step_handler(m, get_desc)

def get_desc(m):
    user_data[m.from_user.id]['desc'] = m.text
    bot.send_message(m.chat.id, "(Opt) *Link*:")
    bot.register_next_step_handler(m, get_link)

def get_link(m):
    uid = m.from_user.id
    user_data[uid]['link'] = m.text if m.text and m.text.startswith('http') else None
    markup = types.InlineKeyboardMarkup(row_width=2)
    for g in groups:
        try:
            c = bot.get_chat(g)
            title = c.title[:15] + '...' if len(c.title)>15 else c.title
        except:
            title = 'Group'
        markup.add(types.InlineKeyboardButton(title, callback_data=f"p_{g}"))
    cap = f"<b>{user_data[uid]['name']}</b>\n{user_data[uid]['price']}\n\n{user_data[uid]['desc']}"
    if isinstance(user_data[uid]['img'], str):
        bot.send_photo(uid, user_data[uid]['img'], caption=cap, parse_mode='HTML', reply_markup=markup)
    else:
        bot.send_photo(uid, user_data[uid]['img'], caption=cap, parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith('p_'))
def send_post(c):
    if c.from_user.id != ADMIN_ID: return
    gid = c.data.split('_',1)[1]
    d = user_data[c.from_user.id]
    cap = f"<b>{d['name']}</b>\n{d['price']}\n\n{d['desc']}"
    kb = types.InlineKeyboardMarkup()
    if d['link']:
        kb.add(types.InlineKeyboardButton("View Product", url=d['link']))
    try:
        if isinstance(d['img'], str):
            bot.send_photo(gid, d['img'], caption=cap, parse_mode='HTML', reply_markup=kb)
        else:
            bot.send_photo(gid, d['img'], caption=cap, parse_mode='HTML', reply_markup=kb)
        bot.answer_callback_query(c.id, "Posted!")
    except:
        bot.answer_callback_query(c.id, "Failed")
    user_data.pop(c.from_user.id, None)

print("Bot starting...")
bot.infinity_polling()
