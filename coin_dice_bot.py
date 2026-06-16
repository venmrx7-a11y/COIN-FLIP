import random
import json
import os
import threading
import re
from datetime import datetime
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ============ FLASK FOR RENDER ============
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
    return {"coin_flips": 0, "dice_rolls": 0, "head_count": 0, "tail_count": 0}

def save_stats(stats):
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def load_force():
    if os.path.exists(FORCE_FILE):
        with open(STRUE_FILE, 'r') as f:
            return json.load(f)
    return {"coin_force": None, "coin_force_count": 0, "dice_force": None}

def save_force(force):
    with open(FORCE_FILE, 'w') as f:
        json.dump(force, f, indent=2)

def load_emojis():
    global PREMIUM_EMOJIS
    try:
        if os.path.exists(EMOJI_FILE):
            with open(EMOJI_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                for key, value in loaded.items():
                    if key not in PREMIUM_EMOJIS:
                        PREMIUM_EMOJIS[key] = value
    except:
        pass

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
    """Har line ke aage aur piche premium emoji lagao"""
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
load_emojis()

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
            "banned": False,
            "coin_wins": 0,
            "coin_losses": 0,
            "dice_plays": 0
        }
        save_users(users)
        return True
    return False

def is_owner(user_id):
    return user_id == OWNER_ID

def is_banned(user_id):
    user = users.get(str(user_id), {})
    return user.get('banned', False)

# ============ OWNER COMMANDS (Hidden from users) ============
async def force_coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /forcecoin head 5 OR /forcecoin tail 3 OR /forcecoin off")
        return
    
    result = context.args[0].lower()
    if result == 'off':
        force["coin_force"] = None
        force["coin_force_count"] = 0
        save_force(force)
        await update.message.reply_text("Force mode OFF!")
        return
    
    if result not in ['head', 'tail']:
        await update.message.reply_text("Use 'head' or 'tail'!")
        return
    
    try:
        count = int(context.args[1])
        if count < 1 or count > 10:
            await update.message.reply_text("Count must be 1-10!")
            return
    except:
        await update.message.reply_text("Invalid count!")
        return
    
    force["coin_force"] = result
    force["coin_force_count"] = count
    save_force(force)
    await update.message.reply_text(f"Next {count} flips will be: {result.upper()}")

async def force_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /forcedice 6 OR /forcedice off")
        return
    
    result = context.args[0].lower()
    if result == 'off':
        force["dice_force"] = None
        save_force(force)
        await update.message.reply_text("Force mode OFF!")
        return
    
    try:
        num = int(result)
        if num < 1 or num > 6:
            await update.message.reply_text("Number must be 1-6!")
            return
    except:
        await update.message.reply_text("Invalid number!")
        return
    
    force["dice_force"] = num
    save_force(force)
    await update.message.reply_text(f"Next dice roll will be: {num}")

async def force_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    current_force = load_force()
    coin_status = "OFF"
    coin_count = 0
    dice_status = "OFF"
    
    if current_force.get("coin_force"):
        coin_status = current_force["coin_force"].upper()
        coin_count = current_force.get("coin_force_count", 0)
    
    if current_force.get("dice_force"):
        dice_status = str(current_force["dice_force"])
    
    await update.message.reply_text(f"Coin Force: {coin_status} ({coin_count} left)\nDice Force: {dice_status}")

async def bot_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    msg_lines = [
        "📊 BOT STATISTICS",
        "━━━━━━━━━━━━━━━━━━",
        f"Users: {len(users)}",
        f"Flips: {stats['coin_flips']}",
        f"Dice: {stats['dice_rolls']}",
        f"Heads: {stats['head_count']}",
        f"Tails: {stats['tail_count']}",
    ]
    await update.message.reply_text("\n".join(msg_lines))

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

# ============ USER COMMANDS ============
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first_name = user.first_name
    register_user(user.id, user.username or "NoUsername", first_name)
    
    msg_lines = [
        "🎲 COIN FLIP & DICE BOT 🎲",
        "━━━━━━━━━━━━━━━━━━",
        f"✨ Welcome, {to_fancy(first_name)}! ✨",
        "",
        "📌 /flipcoin - Flip a coin",
        "📌 /dice - Roll a dice",
        "📌 /mystats - Your stats",
        "━━━━━━━━━━━━━━━━━━"
    ]
    
    message = "\n".join(msg_lines)
    formatted = format_with_double_emojis(message)
    await update.message.reply_text(formatted, parse_mode="HTML")

async def flipcoin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    register_user(user_id, update.effective_user.username or "NoUsername", update.effective_user.first_name)
    
    if is_banned(user_id):
        await update.message.reply_text("❌ You are banned!")
        return
    
    args = context.args
    
    # Load force
    current_force = load_force()
    force_result = None
    if current_force.get("coin_force") and current_force.get("coin_force_count", 0) > 0:
        force_result = current_force["coin_force"]
        current_force["coin_force_count"] -= 1
        if current_force["coin_force_count"] <= 0:
            current_force["coin_force"] = None
        save_force(current_force)
    
    # User prediction
    user_prediction = None
    if len(args) >= 1 and args[0] in ['head', 'tails', 'tail', 'h', 't']:
        user_prediction = args[0]
        if user_prediction in ['h']:
            user_prediction = 'head'
        if user_prediction in ['t', 'tails']:
            user_prediction = 'tail'
    
    # Result
    result = force_result if force_result else random.choice(['head', 'tail'])
    
    # Stats
    stats["coin_flips"] += 1
    if result == 'head':
        stats["head_count"] += 1
    else:
        stats["tail_count"] += 1
    save_stats(stats)
    
    # User stats
    user = users[str(user_id)]
    if user_prediction:
        if user_prediction == result:
            user['coin_wins'] = user.get('coin_wins', 0) + 1
        else:
            user['coin_losses'] = user.get('coin_losses', 0) + 1
    save_users(users)
    
    # Message
    result_text = "HEADS" if result == 'head' else "TAILS"
    fancy_result = to_fancy(result_text)
    
    msg_lines = [
        "🎲 COIN FLIP 🎲",
        "━━━━━━━━━━━━━━━━━━",
        f"🪙 Result: {fancy_result}",
    ]
    
    if user_prediction:
        pred_fancy = to_fancy(user_prediction.upper())
        if user_prediction == result:
            msg_lines.append(f"✅ You predicted {pred_fancy}! 🎉")
        else:
            msg_lines.append(f"❌ You predicted {pred_fancy}! 😢")
    
    msg_lines.append("━━━━━━━━━━━━━━━━━━")
    
    message = "\n".join(msg_lines)
    formatted = format_with_double_emojis(message)
    await update.message.reply_text(formatted, parse_mode="HTML")

async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    register_user(user_id, update.effective_user.username or "NoUsername", update.effective_user.first_name)
    
    if is_banned(user_id):
        await update.message.reply_text("❌ You are banned!")
        return
    
    args = context.args
    
    # Load force
    current_force = load_force()
    force_result = current_force.get("dice_force")
    if force_result:
        current_force["dice_force"] = None
        save_force(current_force)
    
    # User prediction
    user_prediction = None
    if len(args) >= 1:
        try:
            user_prediction = int(args[0])
            if user_prediction < 1 or user_prediction > 6:
                user_prediction = None
        except:
            pass
    
    # Result
    result = force_result if force_result else random.randint(1, 6)
    
    # Stats
    stats["dice_rolls"] += 1
    save_stats(stats)
    
    # User stats
    user = users[str(user_id)]
    user['dice_plays'] = user.get('dice_plays', 0) + 1
    save_users(users)
    
    # Dice emoji
    dice_emoji = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
    fancy_number = to_fancy(str(result))
    
    msg_lines = [
        "🎲 DICE ROLL 🎲",
        "━━━━━━━━━━━━━━━━━━",
        f"{dice_emoji[result]} Result: {fancy_number}",
    ]
    
    if user_prediction:
        if user_prediction == result:
            msg_lines.append(f"✅ You predicted {to_fancy(str(user_prediction))}! 🎉")
        else:
            msg_lines.append(f"❌ You predicted {to_fancy(str(user_prediction))}! 😢")
    
    msg_lines.append("━━━━━━━━━━━━━━━━━━")
    
    message = "\n".join(msg_lines)
    formatted = format_with_double_emojis(message)
    await update.message.reply_text(formatted, parse_mode="HTML")

async def mystats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    register_user(user_id, update.effective_user.username or "NoUsername", update.effective_user.first_name)
    
    user = users[str(user_id)]
    fancy_wins = to_fancy(str(user.get('coin_wins', 0)))
    fancy_losses = to_fancy(str(user.get('coin_losses', 0)))
    fancy_dice = to_fancy(str(user.get('dice_plays', 0)))
    
    msg_lines = [
        "👤 USER STATS 👤",
        "━━━━━━━━━━━━━━━━━━",
        f"📛 {to_fancy(user.get('name', 'Unknown'))}",
        f"🆔 {to_fancy(str(user_id))}",
        "",
        f"🎲 Wins: {fancy_wins}",
        f"🎲 Losses: {fancy_losses}",
        f"🎲 Dice: {fancy_dice}",
        "━━━━━━━━━━━━━━━━━━"
    ]
    
    message = "\n".join(msg_lines)
    formatted = format_with_double_emojis(message)
    await update.message.reply_text(formatted, parse_mode="HTML")

# ============ MAIN ============
def main():
    load_emojis()
    threading.Thread(target=run_flask, daemon=True).start()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # User commands (Users sirf yehi dekh sakte hain)
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("flipcoin", flipcoin_command))
    application.add_handler(CommandHandler("dice", dice_command))
    application.add_handler(CommandHandler("mystats", mystats_command))
    
    # Owner commands (Yeh hidden hain, users ko nahi dikhenge)
    application.add_handler(CommandHandler("forcecoin", force_coin))
    application.add_handler(CommandHandler("forcedice", force_dice))
    application.add_handler(CommandHandler("forcestatus", force_status))
    application.add_handler(CommandHandler("stats", bot_stats))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    
    print("=" * 50)
    print("🎲 COIN FLIP & DICE BOT STARTED")
    print(f"👑 Owner: {OWNER_ID}")
    print("✅ Users see only: /flipcoin, /dice, /mystats")
    print("✅ Premium emojis on every line")
    print("=" * 50)
    
    application.run_polling()

if __name__ == "__main__":
    main()
