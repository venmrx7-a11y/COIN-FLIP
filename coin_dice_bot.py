import random
import json
import os
import threading
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
        with open(FORCE_FILE, 'r') as f:
            return json.load(f)
    return {"coin_force": None, "coin_force_count": 0, "dice_force": None}

def save_force(force):
    with open(FORCE_FILE, 'w') as f:
        json.dump(force, f, indent=2)

users = load_users()
stats = load_stats()
force = load_force()

# ============ FANCY TEXT FUNCTION ============
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

# ============ FORCE COMMANDS (SIRF OWNER) ============
async def force_coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "📝 Usage:\n"
            "/forcecoin head 5 - Next 5 flips will be HEAD\n"
            "/forcecoin tail 3 - Next 3 flips will be TAIL\n"
            "/forcecoin off - Turn off force mode"
        )
        return
    
    result = context.args[0].lower()
    if result == 'off':
        force["coin_force"] = None
        force["coin_force_count"] = 0
        save_force(force)
        await update.message.reply_text("✅ Force mode turned OFF!")
        return
    
    if result not in ['head', 'tail']:
        await update.message.reply_text("❌ Use 'head' or 'tail'!")
        return
    
    try:
        count = int(context.args[1])
        if count < 1 or count > 10:
            await update.message.reply_text("❌ Count must be between 1 and 10!")
            return
    except:
        await update.message.reply_text("❌ Invalid count!")
        return
    
    force["coin_force"] = result
    force["coin_force_count"] = count
    save_force(force)
    
    await update.message.reply_text(f"✅ Next {count} coin flip(s) will be: {result.upper()}")

async def force_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    if len(context.args) < 1:
        await update.message.reply_text(
            "📝 Usage:\n"
            "/forcedice 6 - Next dice roll will be 6\n"
            "/forcedice off - Turn off force mode"
        )
        return
    
    result = context.args[0].lower()
    if result == 'off':
        force["dice_force"] = None
        save_force(force)
        await update.message.reply_text("✅ Force mode turned OFF!")
        return
    
    try:
        num = int(result)
        if num < 1 or num > 6:
            await update.message.reply_text("❌ Number must be between 1 and 6!")
            return
    except:
        await update.message.reply_text("❌ Invalid number!")
        return
    
    force["dice_force"] = num
    save_force(force)
    
    await update.message.reply_text(f"✅ Next dice roll will be: {num}")

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
    
    await update.message.reply_text(
        f"🔧 FORCE MODE STATUS 🔧\n━━━━━━━━━━━━━━━━━━\n\n"
        f"🎲 Coin Force: {coin_status}\n"
        f"📊 Remaining: {coin_count}\n\n"
        f"🎲 Dice Force: {dice_status}"
    )

# ============ COIN FLIP COMMAND ============
async def flipcoin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "NoUsername"
    first_name = update.effective_user.first_name
    
    register_user(user_id, username, first_name)
    
    if is_banned(user_id):
        await update.message.reply_text("❌ You are banned!")
        return
    
    args = context.args
    
    # Load current force settings
    current_force = load_force()
    force_result = None
    
    if current_force.get("coin_force") and current_force.get("coin_force_count", 0) > 0:
        force_result = current_force["coin_force"]
        current_force["coin_force_count"] -= 1
        if current_force["coin_force_count"] <= 0:
            current_force["coin_force"] = None
        save_force(current_force)
    
    # Parse user prediction
    user_prediction = None
    if len(args) >= 1 and args[0] in ['head', 'tails', 'tail', 'h', 't']:
        user_prediction = args[0]
        if user_prediction in ['h']:
            user_prediction = 'head'
        if user_prediction in ['t', 'tails']:
            user_prediction = 'tail'
    
    # Generate result
    if force_result:
        result = force_result
    else:
        result = random.choice(['head', 'tail'])
    
    # Update stats
    stats["coin_flips"] += 1
    if result == 'head':
        stats["head_count"] += 1
    else:
        stats["tail_count"] += 1
    save_stats(stats)
    
    # Update user stats
    user = users[str(user_id)]
    if user_prediction:
        if user_prediction == result:
            user['coin_wins'] = user.get('coin_wins', 0) + 1
        else:
            user['coin_losses'] = user.get('coin_losses', 0) + 1
    save_users(users)
    
    # Create message - NO DEVELOPER NAME
    result_text = "𝐇𝐄𝐀𝐃𝐒" if result == 'head' else "𝐓𝐀𝐈𝐋𝐒"
    fancy_result = to_fancy(result_text)
    
    message = f"""
🎲 𝐂𝐎𝐈𝐍 𝐅𝐋𝐈𝐏 🎲
━━━━━━━━━━━━━━━━━━

🪙 𝐑𝐞𝐬𝐮𝐥𝐭: {fancy_result}
"""
    
    if user_prediction:
        pred_fancy = to_fancy(user_prediction.upper())
        if user_prediction == result:
            message += f"\n✅ 𝐘𝐨𝐮 𝐩𝐫𝐞𝐝𝐢𝐜𝐭𝐞𝐝 {pred_fancy}! 🎉"
        else:
            message += f"\n❌ 𝐘𝐨𝐮 𝐩𝐫𝐞𝐝𝐢𝐜𝐭𝐞𝐝 {pred_fancy}! 😢"
    
    message += f"\n━━━━━━━━━━━━━━━━━━"
    
    await update.message.reply_text(message)

# ============ DICE COMMAND ============
async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "NoUsername"
    first_name = update.effective_user.first_name
    
    register_user(user_id, username, first_name)
    
    if is_banned(user_id):
        await update.message.reply_text("❌ You are banned!")
        return
    
    args = context.args
    
    # Load current force settings
    current_force = load_force()
    force_result = current_force.get("dice_force")
    if force_result:
        current_force["dice_force"] = None
        save_force(current_force)
    
    # Get user prediction
    user_prediction = None
    if len(args) >= 1:
        try:
            user_prediction = int(args[0])
            if user_prediction < 1 or user_prediction > 6:
                user_prediction = None
        except:
            pass
    
    # Generate result
    if force_result:
        result = force_result
    else:
        result = random.randint(1, 6)
    
    # Update stats
    stats["dice_rolls"] += 1
    save_stats(stats)
    
    # Update user stats
    user = users[str(user_id)]
    user['dice_plays'] = user.get('dice_plays', 0) + 1
    save_users(users)
    
    # Dice emoji
    dice_emoji = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
    
    fancy_number = to_fancy(str(result))
    
    message = f"""
🎲 𝐃𝐈𝐂𝐄 𝐑𝐎𝐋𝐋 🎲
━━━━━━━━━━━━━━━━━━

{dice_emoji[result]} 𝐑𝐞𝐬𝐮𝐥𝐭: {fancy_number}
"""
    
    if user_prediction:
        if user_prediction == result:
            message += f"\n✅ 𝐘𝐨𝐮 𝐩𝐫𝐞𝐝𝐢𝐜𝐭𝐞𝐝 {to_fancy(str(user_prediction))}! 🎉"
        else:
            message += f"\n❌ 𝐘𝐨𝐮 𝐩𝐫𝐞𝐝𝐢𝐜𝐭𝐞𝐝 {to_fancy(str(user_prediction))}! 😢"
    
    message += f"\n━━━━━━━━━━━━━━━━━━"
    
    await update.message.reply_text(message)

# ============ MY STATS COMMAND ============
async def mystats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "NoUsername"
    first_name = update.effective_user.first_name
    
    register_user(user_id, username, first_name)
    
    user = users[str(user_id)]
    fancy_wins = to_fancy(str(user.get('coin_wins', 0)))
    fancy_losses = to_fancy(str(user.get('coin_losses', 0)))
    fancy_dice = to_fancy(str(user.get('dice_plays', 0)))
    
    await update.message.reply_text(
        f"👤 𝐔𝐒𝐄𝐑 𝐒𝐓𝐀𝐓𝐒 👤\n━━━━━━━━━━━━━━━━━━\n\n"
        f"📛 {to_fancy(first_name)}\n"
        f"🆔 {to_fancy(str(user_id))}\n\n"
        f"🎲 𝐖𝐢𝐧𝐬: {fancy_wins}\n"
        f"🎲 𝐋𝐨𝐬𝐬𝐞𝐬: {fancy_losses}\n"
        f"🎲 𝐃𝐢𝐜𝐞: {fancy_dice}\n━━━━━━━━━━━━━━━━━━"
    )

# ============ OWNER STATS ============
async def bot_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    await update.message.reply_text(
        f"📊 𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒 📊\n━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 𝐔𝐬𝐞𝐫𝐬: {to_fancy(str(len(users)))}\n"
        f"🎲 𝐅𝐥𝐢𝐩𝐬: {to_fancy(str(stats['coin_flips']))}\n"
        f"🎲 𝐃𝐢𝐜𝐞: {to_fancy(str(stats['dice_rolls']))}\n\n"
        f"🪙 𝐇𝐞𝐚𝐝𝐬: {to_fancy(str(stats['head_count']))}\n"
        f"🪙 𝐓𝐚𝐢𝐥𝐬: {to_fancy(str(stats['tail_count']))}\n"
        f"📈 𝐇𝐞𝐚𝐝𝐬 %: {to_fancy(str(round(stats['head_count']/max(stats['coin_flips'],1)*100, 2)))}\n"
        f"📉 𝐓𝐚𝐢𝐥𝐬 %: {to_fancy(str(round(stats['tail_count']/max(stats['coin_flips'],1)*100, 2)))}\n━━━━━━━━━━━━━━━━━━"
    )

# ============ BAN/UNBAN ============
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
        await update.message.reply_text(f"✅ User {user_id} banned!")

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
        await update.message.reply_text(f"✅ User {user_id} unbanned!")

# ============ START COMMAND ============
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first_name = user.first_name
    
    register_user(user.id, user.username or "NoUsername", first_name)
    
    await update.message.reply_text(
        f"🎲 𝐂𝐎𝐈𝐍 𝐅𝐋𝐈𝐏 & 𝐃𝐈𝐂𝐄 𝐁𝐎𝐓 🎲\n━━━━━━━━━━━━━━━━━━\n\n"
        f"✨ 𝐖𝐞𝐥𝐜𝐨𝐦𝐞, {to_fancy(first_name)}! ✨\n\n"
        f"📌 `/flipcoin` - 𝐅𝐥𝐢𝐩 𝐚 𝐜𝐨𝐢𝐧\n"
        f"📌 `/dice` - 𝐑𝐨𝐥𝐥 𝐚 𝐝𝐢𝐜𝐞\n"
        f"📌 `/mystats` - 𝐘𝐨𝐮𝐫 𝐬𝐭𝐚𝐭𝐬\n━━━━━━━━━━━━━━━━━━\n👑 @TITANXSELLER"
    )

# ============ MAIN ============
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # User commands (SIRF YAHI DO COMMAND)
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("flipcoin", flipcoin_command))
    application.add_handler(CommandHandler("dice", dice_command))
    application.add_handler(CommandHandler("mystats", mystats_command))
    
    # Owner commands (YEH SIRF OWNER KE LIYE, USERS KO NAHI DIKHENGE)
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
    print("✅ No developer name in results")
    print("=" * 50)
    
    application.run_polling()

if __name__ == "__main__":
    main()
