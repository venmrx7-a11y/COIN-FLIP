import random
import json
import os
import threading
from datetime import datetime
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

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

USERS_FILE = "users.json"
STATS_FILE = "stats.json"
FORCE_FILE = "force.json"
EMOJI_FILE = "emojis.json"

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
    return {"user_forces": {}}

def save_force(force):
    with open(FORCE_FILE, 'w') as f:
        json.dump(force, f, indent=2)

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

def is_owner(user_id):
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

# ============ OWNER COMMANDS ============
async def set_user_force(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner: /userforce USER_ID head 5"""
    if update.effective_user.id != OWNER_ID:
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "Usage:\n"
            "/userforce USER_ID head 5 - User ko 5 baar HEAD milega\n"
            "/userforce USER_ID tail 3 - User ko 3 baar TAIL milega\n"
            "/userforce USER_ID dice 6 - User ko dice 6 milega\n"
            "/userforce USER_ID off - User ka force hatana"
        )
        return
    
    user_id = context.args[0]
    force_type = context.args[1].lower()
    try:
        count = int(context.args[2])
    except:
        await update.message.reply_text("Invalid count!")
        return
    
    if user_id not in users:
        await update.message.reply_text(f"User {user_id} not found!")
        return
    
    if force_type not in ['head', 'tail', 'dice']:
        await update.message.reply_text("Use: head, tail, or dice")
        return
    
    if count < 1 or count > 10:
        await update.message.reply_text("Count must be 1-10!")
        return
    
    if 'user_forces' not in force:
        force['user_forces'] = {}
    
    force['user_forces'][user_id] = {
        "type": force_type,
        "count": count,
        "remaining": count
    }
    save_force(force)
    
    await update.message.reply_text(f"User {user_id} will get {force_type.upper()} {count} times!")

async def remove_user_force(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner: /removeforce USER_ID"""
    if update.effective_user.id != OWNER_ID:
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /removeforce USER_ID")
        return
    
    user_id = context.args[0]
    if 'user_forces' in force and user_id in force['user_forces']:
        del force['user_forces'][user_id]
        save_force(force)
        await update.message.reply_text(f"Force removed for user {user_id}")
    else:
        await update.message.reply_text(f"No force found for user {user_id}")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    if not users:
        await update.message.reply_text("No users found.")
        return
    
    msg = "👥 USERS LIST\n━━━━━━━━━━━━━━━━━━\n"
    for uid, u in users.items():
        status = "🚫 BANNED" if u.get('banned') else "✅ ACTIVE"
        msg += f"🆔 {uid}\n📛 @{u.get('username', 'None')}\n📌 {status}\n\n"
    
    await update.message.reply_text(msg)

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /ban USER_ID")
        return
    user_id = context.args[0]
    if user_id in users:
        users[user_id]['banned'] = True
        save_users(users)
        await update.message.reply_text(f"User {user_id} banned!")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /unban USER_ID")
        return
    user_id = context.args[0]
    if user_id in users:
        users[user_id]['banned'] = False
        save_users(users)
        await update.message.reply_text(f"User {user_id} unbanned!")

async def owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    msg_lines = [
        "📊 BOT STATISTICS",
        "━━━━━━━━━━━━━━━━━━",
        f"👥 Users: {len(users)}",
        f"🎲 Coin Flips: {stats['coin_flips']}",
        f"🎲 Dice Rolls: {stats['dice_rolls']}",
        f"📋 Forced Users: {len(force.get('user_forces', {}))}"
    ]
    await update.message.reply_text("\n".join(msg_lines))

# ============ USER COMMANDS ============
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user.id, user.username or "NoUsername", user.first_name)
    
    msg_lines = [
        "🎲 COIN FLIP & DICE BOT 🎲",
        "━━━━━━━━━━━━━━━━━━",
        f"✨ Welcome, {to_fancy(user.first_name)}! ✨",
        "",
        "📌 /flipcoin - Flip a coin",
        "📌 /dice - Roll a dice",
        "━━━━━━━━━━━━━━━━━━"
    ]
    
    message = "\n".join(msg_lines)
    formatted = format_with_double_emojis(message)
    await update.message.reply_text(formatted, parse_mode="HTML")

async def flipcoin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_id_str = str(user_id)
    username = update.effective_user.username or "NoUsername"
    first_name = update.effective_user.first_name
    
    register_user(user_id, username, first_name)
    
    if is_banned(user_id):
        await update.message.reply_text("❌ You are banned!")
        return
    
    # Check if user has forced result
    user_force = force.get('user_forces', {}).get(user_id_str)
    result = None
    
    if user_force and user_force['remaining'] > 0:
        result = user_force['type']
        user_force['remaining'] -= 1
        if user_force['remaining'] <= 0:
            del force['user_forces'][user_id_str]
        save_force(force)
    
    if not result:
        result = get_next_coin()
    
    # Stats
    stats["coin_flips"] += 1
    save_stats(stats)
    
    # Result text
    fancy_result = to_fancy(result)
    
    msg_lines = [
        "🪙 COIN FLIP 🪙",
        "━━━━━━━━━━━━━━━━━━",
        f"Result: {fancy_result}",
        "━━━━━━━━━━━━━━━━━━"
    ]
    
    message = "\n".join(msg_lines)
    formatted = format_with_double_emojis(message)
    await update.message.reply_text(formatted, parse_mode="HTML")

async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_id_str = str(user_id)
    username = update.effective_user.username or "NoUsername"
    first_name = update.effective_user.first_name
    
    register_user(user_id, username, first_name)
    
    if is_banned(user_id):
        await update.message.reply_text("❌ You are banned!")
        return
    
    # Check if user has forced dice result
    user_force = force.get('user_forces', {}).get(user_id_str)
    
    if user_force and user_force['type'] == 'dice' and user_force['remaining'] > 0:
        result = user_force['type']  # This will be 'dice', but we need number
        user_force['remaining'] -= 1
        if user_force['remaining'] <= 0:
            del force['user_forces'][user_id_str]
        save_force(force)
        # For dice, we need the count as the number
        dice_number = user_force['count']
    else:
        dice_number = random.randint(1, 6)
    
    # Stats
    stats["dice_rolls"] += 1
    save_stats(stats)
    
    # Dice emoji
    dice_emoji = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
    fancy_number = to_fancy(str(dice_number))
    
    msg_lines = [
        "🎲 DICE ROLL 🎲",
        "━━━━━━━━━━━━━━━━━━",
        f"{dice_emoji[dice_number]} Result: {fancy_number}",
        "━━━━━━━━━━━━━━━━━━"
    ]
    
    message = "\n".join(msg_lines)
    formatted = format_with_double_emojis(message)
    await update.message.reply_text(formatted, parse_mode="HTML")

# ============ MAIN ============
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # User commands (sirf yehi dikhenge users ko)
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("flipcoin", flipcoin_command))
    application.add_handler(CommandHandler("dice", dice_command))
    
    # Owner commands (hidden)
    application.add_handler(CommandHandler("userforce", set_user_force))
    application.add_handler(CommandHandler("removeforce", remove_user_force))
    application.add_handler(CommandHandler("users", list_users))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("stats", owner_stats))
    
    print("=" * 50)
    print("🎲 COIN FLIP & DICE BOT STARTED")
    print(f"👑 Owner: {OWNER_ID}")
    print("✅ Coin Pattern: HEAD, TAIL, TAIL, HEAD, HEAD, HEAD, TAIL...")
    print("✅ Users see only: /flipcoin and /dice")
    print("=" * 50)
    
    application.run_polling()

if __name__ == "__main__":
    main()
