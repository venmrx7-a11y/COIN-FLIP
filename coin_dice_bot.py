import random
import json
import os
import threading
from datetime import datetime
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ============ FLASK ============
flask_app = Flask(__name__)

@flask_app.route('/')
@flask_app.route('/health')
def health():
    return "Bot is running!", 200

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    flask_app.run(host='0.0.0.0', port=port)

# ============ CONFIG ============
BOT_TOKEN = "8592467504:AAEm-p2jCYnWUaq4Yy8MhhMSDI2eTY_Xc6M"
OWNER_ID = 8986441675
MAIN_GROUP_LINK = "https://t.me/+0NcOgFZ-qnE4OTVl"

USERS_FILE = "users.json"
ADMINS_FILE = "admins.json"
OWNERS_FILE = "owners.json"
STATS_FILE = "stats.json"
FORCE_FILE = "force.json"

# ============ FIXED COIN PATTERN ============
COIN_PATTERN = ['HEAD', 'TAIL', 'TAIL', 'HEAD', 'HEAD', 'HEAD', 'TAIL', 'HEAD', 'HEAD', 'TAIL', 'TAIL', 'HEAD', 'TAIL']
pattern_index = 0

# ============ PREMIUM EMOJIS ============
PREMIUM_EMOJIS = {
    "verified": {"id": "6147565374289220368", "fallback": "✅", "added_by": "system", "date": "2024-01-01"},
    "flex": {"id": "6147464060305676048", "fallback": "😎", "added_by": "system", "date": "2024-01-01"},
    "blue_verification": {"id": "6147524086768604985", "fallback": "💎", "added_by": "system", "date": "2024-01-01"},
    "frozen": {"id": "5449449325434266744", "fallback": "❄️", "added_by": "system", "date": "2024-01-01"},
    "crying": {"id": "6273840152980755328", "fallback": "😭", "added_by": "system", "date": "2024-01-01"},
    "smiling": {"id": "6276057176444246654", "fallback": "🙂", "added_by": "system", "date": "2024-01-01"},
    "seeing_up": {"id": "6273997026661241933", "fallback": "😋", "added_by": "system", "date": "2024-01-01"},
    "teeth": {"id": "6273726078649372769", "fallback": "😁", "added_by": "system", "date": "2024-01-01"},
    "done": {"id": "6274007313107915274", "fallback": "👍", "added_by": "system", "date": "2024-01-01"},
    "blue_badge": {"id": "5978776771623914876", "fallback": "🟫", "added_by": "system", "date": "2024-01-01"},
    "black_badge": {"id": "5978686323907628843", "fallback": "🔸", "added_by": "system", "date": "2024-01-01"},
    "busy_tag": {"id": "5852873584912896283", "fallback": "🟧", "added_by": "system", "date": "2024-01-01"},
    "instagram": {"id": "5895297528106061174", "fallback": "🌐", "added_by": "system", "date": "2024-01-01"},
    "telegram": {"id": "5895735846698487922", "fallback": "🌐", "added_by": "system", "date": "2024-01-01"},
    "whatsapp": {"id": "5895343514320899727", "fallback": "🌐", "added_by": "system", "date": "2024-01-01"},
    "india": {"id": "5913754823643107921", "fallback": "🇮🇳", "added_by": "system", "date": "2024-01-01"},
    "dollar": {"id": "5197434882321567830", "fallback": "💵", "added_by": "system", "date": "2024-01-01"},
    "top": {"id": "5463071033256848094", "fallback": "🔝", "added_by": "system", "date": "2024-01-01"},
    "bro": {"id": "5463256910851546817", "fallback": "🤝", "added_by": "system", "date": "2024-01-01"},
    "yes": {"id": "5463423955014529788", "fallback": "👌", "added_by": "system", "date": "2024-01-01"},
    "lock": {"id": "5465443379917629504", "fallback": "🔓", "added_by": "system", "date": "2024-01-01"},
    "good": {"id": "5465465194056525619", "fallback": "👍", "added_by": "system", "date": "2024-01-01"},
    "sigma": {"id": "6235620067942341623", "fallback": "🥃", "added_by": "system", "date": "2024-01-01"},
    "don": {"id": "6235717714023814969", "fallback": "🍂", "added_by": "system", "date": "2024-01-01"},
    "skills": {"id": "6235593671073339928", "fallback": "💀", "added_by": "system", "date": "2024-01-01"},
    "heart": {"id": "6147617184479711380", "fallback": "❤️‍🔥", "added_by": "system", "date": "2024-01-01"},
    "stars": {"id": "6235403472741603087", "fallback": "⭐", "added_by": "system", "date": "2024-01-01"},
    "github": {"id": "5346181118884331907", "fallback": "📱", "added_by": "system", "date": "2024-01-01"},
    "motion": {"id": "5971944878815317190", "fallback": "💠", "added_by": "system", "date": "2024-01-01"},
}

# ============ FILE FUNCTIONS ============
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_admins():
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, 'r') as f:
            return json.load(f)
    return [OWNER_ID]

def save_admins(admins):
    with open(ADMINS_FILE, 'w') as f:
        json.dump(admins, f, indent=2)

def load_owners():
    if os.path.exists(OWNERS_FILE):
        with open(OWNERS_FILE, 'r') as f:
            return json.load(f)
    return [OWNER_ID]

def save_owners(owners):
    with open(OWNERS_FILE, 'w') as f:
        json.dump(owners, f, indent=2)

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    return {"coin_flips": 0, "dice_rolls": 0}

def save_stats(stats):
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def load_force():
    if os.path.exists(FORCE_FILE):
        with open(FORCE_FILE, 'r') as f:
            return json.load(f)
    return {"coin_force": None, "coin_force_count": 0, "dice_force": None}

def save_force(force):
    with open(FORCE_FILE, 'w') as f:
        json.dump(force, f, indent=2)

admins = load_admins()
owners = load_owners()
users = load_users()
stats = load_stats()
force = load_force()

# ============ STYLISH TEXT ============
def to_fancy(text):
    fancy_map = {
        'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅', 'G': '𝐆', 'H': '𝐇', 'I': '𝐈',
        'J': '𝐉', 'K': '𝐊', 'L': '𝐋', 'M': '𝐌', 'N': '𝐍', 'O': '𝐎', 'P': '𝐏', 'Q': '𝐐', 'R': '𝐑',
        'S': '𝐒', 'T': '𝐓', 'U': '𝐔', 'V': '𝐕', 'W': '𝐖', 'X': '𝐗', 'Y': '𝐘', 'Z': '𝐙',
        'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞', 'f': '𝐟', 'g': '𝐠', 'h': '𝐡', 'i': '𝐢',
        'j': '𝐣', 'k': '𝐤', 'l': '𝐥', 'm': '𝐦', 'n': '𝐧', 'o': '𝐨', 'p': '𝐩', 'q': '𝐪', 'r': '𝐫',
        's': '𝐬', 't': '𝐭', 'u': '𝐮', 'v': '𝐯', 'w': '𝐰', 'x': '𝐱', 'y': '𝐲', 'z': '𝐳',
        '0': '𝟎', '1': '𝟏', '2': '𝟐', '3': '𝟑', '4': '𝟒', '5': '𝟓', '6': '𝟔', '7': '𝟕', '8': '𝟖', '9': '𝟗'
    }
    return ''.join(fancy_map.get(c, c) for c in text)

# ============ EMOJI FUNCTIONS ============
def get_emoji_html(name):
    if name in PREMIUM_EMOJIS:
        data = PREMIUM_EMOJIS[name]
        return f'<tg-emoji emoji-id="{data["id"]}">{data["fallback"]}</tg-emoji>'
    return ""

def get_random_emoji():
    names = list(PREMIUM_EMOJIS.keys())
    if not names:
        return ""
    random_name = random.choice(names)
    return get_emoji_html(random_name)

def format_with_double_emojis(text):
    lines = text.split('\n')
    formatted_lines = []
    for line in lines:
        if line.strip():
            left_emoji = get_random_emoji()
            right_emoji = get_random_emoji()
            formatted_lines.append(f"{left_emoji} {line} {right_emoji}")
        else:
            formatted_lines.append(line)
    return '\n'.join(formatted_lines)

def register_user(user_id, username, first_name):
    if str(user_id) not in users:
        users[str(user_id)] = {
            "id": user_id,
            "username": username,
            "name": first_name,
            "joined": str(datetime.now()),
            "banned": False
        }
        save_users(users)
        return True
    return False

def is_admin(user_id):
    return user_id in admins

def is_owner(user_id):
    return user_id in owners

def is_original_owner(user_id):
    return user_id == OWNER_ID

def is_banned(user_id):
    user = users.get(str(user_id), {})
    return user.get('banned', False)

# ============ GET NEXT COIN RESULT ============
def get_next_coin():
    global pattern_index
    result = COIN_PATTERN[pattern_index % len(COIN_PATTERN)]
    pattern_index += 1
    return result

# ============ ADD OWNER ============
async def add_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ 𝐎𝐧𝐥𝐲 𝐨𝐫𝐢𝐠𝐢𝐧𝐚𝐥 𝐨𝐰𝐧𝐞𝐫 𝐜𝐚𝐧 𝐚𝐝𝐝!")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("𝐔𝐬𝐚𝐠𝐞: `/addowner 𝐔𝐒𝐄𝐑_𝐈𝐃`", parse_mode="Markdown")
        return
    
    try:
        user_id = int(context.args[0])
        if user_id in owners:
            await update.message.reply_text(f"✅ {to_fancy(str(user_id))} 𝐢𝐬 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐚𝐧 𝐨𝐰𝐧𝐞𝐫!")
            return
        owners.append(user_id)
        save_owners(owners)
        await update.message.reply_text(f"✅ {to_fancy(str(user_id))} 𝐢𝐬 𝐧𝐨𝐰 𝐚𝐧 𝐨𝐰𝐧𝐞𝐫!")
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="🎉 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐰 𝐚𝐧 𝐨𝐰𝐧𝐞𝐫!\n\n📌 `/forcecoin head 5` - 𝐅𝐨𝐫𝐜𝐞 𝐡𝐞𝐚𝐝\n📌 `/forcecoin tail 3` - 𝐅𝐨𝐫𝐜𝐞 𝐭𝐚𝐢𝐥\n📌 `/forcedice 6` - 𝐅𝐨𝐫𝐜𝐞 𝐝𝐢𝐜𝐞"
            )
        except:
            pass
    except:
        await update.message.reply_text("❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐈𝐃!")

# ============ REMOVE OWNER ============
async def remove_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /removeowner USER_ID")
        return
    
    try:
        user_id = int(context.args[0])
        if user_id == OWNER_ID:
            await update.message.reply_text("❌ 𝐂𝐚𝐧𝐧𝐨𝐭 𝐫𝐞𝐦𝐨𝐯𝐞 𝐨𝐫𝐢𝐠𝐢𝐧𝐚𝐥 𝐨𝐰𝐧𝐞𝐫!")
            return
        if user_id in owners:
            owners.remove(user_id)
            save_owners(owners)
            await update.message.reply_text(f"✅ {to_fancy(str(user_id))} 𝐫𝐞𝐦𝐨𝐯𝐞𝐝!")
        else:
            await update.message.reply_text(f"❌ {to_fancy(str(user_id))} 𝐧𝐨𝐭 𝐨𝐰𝐧𝐞𝐫!")
    except:
        await update.message.reply_text("❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐈𝐃!")

# ============ FORCE COIN (Only Owners) ============
async def force_coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("𝐔𝐬𝐚𝐠𝐞:\n/forcecoin head 5\n/forcecoin tail 3\n/forcecoin off")
        return
    
    result = context.args[0].lower()
    if result == 'off':
        force["coin_force"] = None
        force["coin_force_count"] = 0
        save_force(force)
        await update.message.reply_text("✅ 𝐅𝐨𝐫𝐜𝐞 𝐎𝐅𝐅!")
        return
    
    if result not in ['head', 'tail']:
        await update.message.reply_text("❌ 𝐔𝐬𝐞 'head' 𝐨𝐫 'tail'!")
        return
    
    try:
        count = int(context.args[1])
        if count < 1 or count > 10:
            await update.message.reply_text("❌ 𝐂𝐨𝐮𝐧𝐭 𝟏-𝟏𝟎!")
            return
    except:
        await update.message.reply_text("❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐜𝐨𝐮𝐧𝐭!")
        return
    
    force["coin_force"] = result
    force["coin_force_count"] = count
    save_force(force)
    
    await update.message.reply_text(f"✅ {to_fancy(str(count))} {to_fancy(result.upper())} 𝐚𝐚𝐲𝐞𝐧𝐠𝐞!")

# ============ FORCE DICE (Only Owners) ============
async def force_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("𝐔𝐬𝐚𝐠𝐞:\n/forcedice 6\n/forcedice off")
        return
    
    result = context.args[0].lower()
    if result == 'off':
        force["dice_force"] = None
        save_force(force)
        await update.message.reply_text("✅ 𝐅𝐨𝐫𝐜𝐞 𝐎𝐅𝐅!")
        return
    
    try:
        num = int(result)
        if num < 1 or num > 6:
            await update.message.reply_text("❌ 𝟏-𝟔 𝐝𝐚𝐚𝐥𝐨!")
            return
    except:
        await update.message.reply_text("❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝!")
        return
    
    force["dice_force"] = num
    save_force(force)
    await update.message.reply_text(f"✅ 𝐍𝐞𝐱𝐭 𝐝𝐢𝐜𝐞: {to_fancy(str(num))}")

# ============ FORCE STATUS ============
async def force_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    
    coin_status = "OFF"
    coin_count = 0
    dice_status = "OFF"
    
    if force.get("coin_force"):
        coin_status = force["coin_force"].upper()
        coin_count = force.get("coin_force_count", 0)
    
    if force.get("dice_force"):
        dice_status = str(force["dice_force"])
    
    await update.message.reply_text(
        f"🔧 𝐅𝐎𝐑𝐂𝐄 𝐒𝐓𝐀𝐓𝐔𝐒\n━━━━━━━━━━━━━━━━━━\n\n"
        f"🪙 𝐂𝐨𝐢𝐧: {coin_status} ({coin_count} 𝐥𝐞𝐟𝐭)\n"
        f"🎲 𝐃𝐢𝐜𝐞: {dice_status}"
    )

# ============ APPROVE ADMIN ============
async def approve_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ 𝐎𝐧𝐥𝐲 𝐨𝐰𝐧𝐞𝐫𝐬 𝐜𝐚𝐧 𝐚𝐩𝐩𝐫𝐨𝐯𝐞!")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("𝐔𝐬𝐚𝐠𝐞: `/approve 𝐔𝐒𝐄𝐑_𝐈𝐃`", parse_mode="Markdown")
        return
    
    try:
        user_id = int(context.args[0])
        if user_id in admins:
            await update.message.reply_text(f"✅ {to_fancy(str(user_id))} 𝐢𝐬 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐚𝐝𝐦𝐢𝐧!")
            return
        admins.append(user_id)
        save_admins(admins)
        await update.message.reply_text(f"✅ {to_fancy(str(user_id))} 𝐢𝐬 𝐧𝐨𝐰 𝐚𝐧 𝐚𝐝𝐦𝐢𝐧!")
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="🎉 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐰 𝐚𝐧 𝐚𝐝𝐦𝐢𝐧!\n\n📌 `/flipcoin` - 𝐅𝐥𝐢𝐩\n📌 `/dice` - 𝐑𝐨𝐥𝐥"
            )
        except:
            pass
    except:
        await update.message.reply_text("❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐈𝐃!")

async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /removeadmin USER_ID")
        return
    try:
        user_id = int(context.args[0])
        if user_id == OWNER_ID:
            await update.message.reply_text("❌ 𝐂𝐚𝐧𝐧𝐨𝐭 𝐫𝐞𝐦𝐨𝐯𝐞 𝐨𝐰𝐧𝐞𝐫!")
            return
        if user_id in admins:
            admins.remove(user_id)
            save_admins(admins)
            await update.message.reply_text(f"✅ {to_fancy(str(user_id))} 𝐫𝐞𝐦𝐨𝐯𝐞𝐝!")
        else:
            await update.message.reply_text(f"❌ {to_fancy(str(user_id))} 𝐧𝐨𝐭 𝐚𝐝𝐦𝐢𝐧!")
    except:
        await update.message.reply_text("❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐈𝐃!")

# ============ BAN/UNBAN ============
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /ban USER_ID")
        return
    user_id = context.args[0]
    if user_id in users:
        users[user_id]['banned'] = True
        save_users(users)
        await update.message.reply_text(f"✅ {to_fancy(user_id)} 𝐛𝐚𝐧𝐧𝐞𝐝!")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /unban USER_ID")
        return
    user_id = context.args[0]
    if user_id in users:
        users[user_id]['banned'] = False
        save_users(users)
        await update.message.reply_text(f"✅ {to_fancy(user_id)} 𝐮𝐧𝐛𝐚𝐧𝐧𝐞𝐝!")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    if not users:
        await update.message.reply_text("📭 𝐍𝐨 𝐮𝐬𝐞𝐫𝐬.")
        return
    msg = "👥 𝐔𝐒𝐄𝐑𝐒\n━━━━━━━━━━━━━━━━━━\n"
    for uid, u in users.items():
        status = "🚫" if u.get('banned') else "✅"
        admin_tag = "👑" if int(uid) in admins else ""
        owner_tag = "⭐" if int(uid) in owners else ""
        msg += f"{status} {to_fancy(uid)}\n📛 @{u.get('username', 'None')} {admin_tag}{owner_tag}\n\n"
    await update.message.reply_text(msg)

async def owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    msg = f"""
📊 𝐒𝐓𝐀𝐓𝐒
━━━━━━━━━━━━━━━━━━
👥 𝐔𝐬𝐞𝐫𝐬: {to_fancy(str(len(users)))}
👑 𝐀𝐝𝐦𝐢𝐧𝐬: {to_fancy(str(len(admins)))}
⭐ 𝐎𝐰𝐧𝐞𝐫𝐬: {to_fancy(str(len(owners)))}
🎲 𝐅𝐥𝐢𝐩𝐬: {to_fancy(str(stats['coin_flips']))}
🎲 𝐃𝐢𝐜𝐞: {to_fancy(str(stats['dice_rolls']))}
━━━━━━━━━━━━━━━━━━
"""
    await update.message.reply_text(msg)

# ============ USER COMMANDS ============
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_type = update.effective_chat.type
    
    if chat_type == 'private':
        msg = f"""
⚠️ 𝐎𝐍𝐋𝐘 𝐖𝐎𝐑𝐊𝐒 𝐈𝐍 𝐆𝐑𝐎𝐔𝐏
━━━━━━━━━━━━━━━━━━

🔗 𝐉𝐨𝐢𝐧: {MAIN_GROUP_LINK}
"""
        formatted = format_with_double_emojis(msg)
        await update.message.reply_text(formatted, parse_mode="HTML")
        return
    
    register_user(user.id, user.username or "NoUsername", user.first_name)
    
    msg = f"""
🎲 𝐂𝐎𝐈𝐍 𝐅𝐋𝐈𝐏 & 𝐃𝐈𝐂𝐄 🎲
━━━━━━━━━━━━━━━━━━

✨ {to_fancy(f'𝐖𝐞𝐥𝐜𝐨𝐦𝐞, {user.first_name}!')} ✨

📌 `/flipcoin` - 𝐅𝐥𝐢𝐩
📌 `/dice` - 𝐑𝐨𝐥𝐥
━━━━━━━━━━━━━━━━━━
"""
    formatted = format_with_double_emojis(msg)
    await update.message.reply_text(formatted, parse_mode="HTML")

async def flipcoin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        msg = "❌ 𝐀𝐝𝐦𝐢𝐧 𝐨𝐧𝐥𝐲!"
        await update.message.reply_text(msg)
        return
    
    register_user(user_id, update.effective_user.username or "NoUsername", update.effective_user.first_name)
    
    if is_banned(user_id):
        await update.message.reply_text("❌ 𝐁𝐚𝐧𝐧𝐞𝐝!")
        return
    
    # Check global force (set by owners)
    result = None
    if force.get("coin_force") and force.get("coin_force_count", 0) > 0:
        result = force["coin_force"]
        force["coin_force_count"] -= 1
        if force["coin_force_count"] <= 0:
            force["coin_force"] = None
        save_force(force)
    
    if not result:
        result = get_next_coin()
    
    stats["coin_flips"] += 1
    save_stats(stats)
    
    msg = f"""
🪙 𝐂𝐎𝐈𝐍 𝐅𝐋𝐈𝐏 🪙
━━━━━━━━━━━━━━━━━━

{to_fancy(f'𝐑𝐞𝐬𝐮𝐥𝐭: {result}')}

━━━━━━━━━━━━━━━━━━
"""
    formatted = format_with_double_emojis(msg)
    await update.message.reply_text(formatted, parse_mode="HTML")

async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ 𝐀𝐝𝐦𝐢𝐧 𝐨𝐧𝐥𝐲!")
        return
    
    register_user(user_id, update.effective_user.username or "NoUsername", update.effective_user.first_name)
    
    if is_banned(user_id):
        await update.message.reply_text("❌ 𝐁𝐚𝐧𝐧𝐞𝐝!")
        return
    
    # Check global dice force
    dice_number = force.get("dice_force")
    if dice_number:
        force["dice_force"] = None
        save_force(force)
    else:
        dice_number = random.randint(1, 6)
    
    stats["dice_rolls"] += 1
    save_stats(stats)
    
    dice_emoji = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
    
    msg = f"""
🎲 𝐃𝐈𝐂𝐄 𝐑𝐎𝐋𝐋 🎲
━━━━━━━━━━━━━━━━━━

{dice_emoji[dice_number]} {to_fancy(f'𝐑𝐞𝐬𝐮𝐥𝐭: {dice_number}')}

━━━━━━━━━━━━━━━━━━
"""
    formatted = format_with_double_emojis(msg)
    await update.message.reply_text(formatted, parse_mode="HTML")

# ============ UNKNOWN COMMANDS ============
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return

# ============ MAIN ============
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # User commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("flipcoin", flipcoin_command))
    application.add_handler(CommandHandler("dice", dice_command))
    
    # Owner management
    application.add_handler(CommandHandler("addowner", add_owner))
    application.add_handler(CommandHandler("removeowner", remove_owner))
    
    # Admin management
    application.add_handler(CommandHandler("approve", approve_admin))
    application.add_handler(CommandHandler("removeadmin", remove_admin))
    
    # Owner force commands
    application.add_handler(CommandHandler("forcecoin", force_coin))
    application.add_handler(CommandHandler("forcedice", force_dice))
    application.add_handler(CommandHandler("forcestatus", force_status))
    
    # Owner management commands
    application.add_handler(CommandHandler("users", list_users))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("stats", owner_stats))
    
    # Unknown commands - ignore
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    print("=" * 50)
    print("🎲 COIN FLIP & DICE BOT STARTED")
    print(f"👑 Original Owner: {OWNER_ID}")
    print(f"⭐ Owners: {owners}")
    print(f"👑 Admins: {admins}")
    print("✅ /addowner - Add new owner")
    print("✅ /forcecoin head 5 - Force coin")
    print("✅ /forcecoin tail 3 - Force tail")
    print("✅ /forcedice 6 - Force dice")
    print("=" * 50)
    
    application.run_polling()

if __name__ == "__main__":
    main()
