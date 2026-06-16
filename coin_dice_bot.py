import random
import re
import json
import os
import threading
from datetime import datetime
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

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
ADMIN_IDS = [OWNER_ID]

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

# ============ FORCE COMMANDS (SIRF OWNER KE LIYE) ============
async def force_coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner command: /forcecoin head 5  or  /forcecoin tail 3"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ 𝐎𝐧𝐥𝐲 𝐨𝐰𝐧𝐞𝐫 𝐜𝐚𝐧 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "📝 𝐔𝐬𝐚𝐠𝐞:\n"
            "`/forcecoin head 5` - 𝐍𝐞𝐱𝐭 𝟓 𝐟𝐥𝐢𝐩𝐬 𝐰𝐢𝐥𝐥 𝐛𝐞 𝐇𝐄𝐀𝐃\n"
            "`/forcecoin tail 3` - 𝐍𝐞𝐱𝐭 𝟑 𝐟𝐥𝐢𝐩𝐬 𝐰𝐢𝐥𝐥 𝐛𝐞 𝐓𝐀𝐈𝐋\n"
            "`/forcecoin off` - 𝐓𝐮𝐫𝐧 𝐨𝐟𝐟 𝐟𝐨𝐫𝐜𝐞 𝐦𝐨𝐝𝐞",
            parse_mode="Markdown"
        )
        return
    
    result = context.args[0].lower()
    if result == 'off':
        force["coin_force"] = None
        force["coin_force_count"] = 0
        save_force(force)
        await update.message.reply_text("✅ 𝐅𝐨𝐫𝐜𝐞 𝐦𝐨𝐝𝐞 𝐭𝐮𝐫𝐧𝐞𝐝 𝐎𝐅𝐅! 𝐍𝐨𝐰 𝐟𝐥𝐢𝐩𝐬 𝐰𝐢𝐥𝐥 𝐛𝐞 𝐫𝐚𝐧𝐝𝐨𝐦.")
        return
    
    if result not in ['head', 'tail']:
        await update.message.reply_text("❌ 𝐔𝐬𝐞 `head` 𝐨𝐫 `tail`!")
        return
    
    try:
        count = int(context.args[1])
        if count < 1 or count > 10:
            await update.message.reply_text("❌ 𝐂𝐨𝐮𝐧𝐭 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐛𝐞𝐭𝐰𝐞𝐞𝐧 𝟏 𝐚𝐧𝐝 𝟏𝟎!")
            return
    except:
        await update.message.reply_text("❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐜𝐨𝐮𝐧𝐭!")
        return
    
    force["coin_force"] = result
    force["coin_force_count"] = count
    save_force(force)
    
    await update.message.reply_text(
        f"✅ 𝐅𝐨𝐫𝐜𝐞 𝐦𝐨𝐝𝐞 𝐚𝐜𝐭𝐢𝐯𝐚𝐭𝐞𝐝!\n\n"
        f"🎲 𝐍𝐞𝐱𝐭 {count} 𝐜𝐨𝐢𝐧 𝐟𝐥𝐢𝐩(𝐬) 𝐰𝐢𝐥𝐥 𝐛𝐞: **{result.upper()}**\n"
        f"⚠️ 𝐔𝐬𝐞𝐫𝐬 𝐰𝐢𝐥𝐥 𝐧𝐨𝐭 𝐤𝐧𝐨𝐰 𝐭𝐡𝐢𝐬!"
    )

async def force_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner command: /forcedice 6  or  /forcedice off"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ 𝐎𝐧𝐥𝐲 𝐨𝐰𝐧𝐞𝐫 𝐜𝐚𝐧 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬!")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text(
            "📝 𝐔𝐬𝐚𝐠𝐞:\n"
            "`/forcedice 6` - 𝐍𝐞𝐱𝐭 𝐝𝐢𝐜𝐞 𝐫𝐨𝐥𝐥 𝐰𝐢𝐥𝐥 𝐛𝐞 𝟔\n"
            "`/forcedice off` - 𝐓𝐮𝐫𝐧 𝐨𝐟𝐟 𝐟𝐨𝐫𝐜𝐞 𝐦𝐨𝐝𝐞",
            parse_mode="Markdown"
        )
        return
    
    result = context.args[0].lower()
    if result == 'off':
        force["dice_force"] = None
        save_force(force)
        await update.message.reply_text("✅ 𝐅𝐨𝐫𝐜𝐞 𝐦𝐨𝐝𝐞 𝐭𝐮𝐫𝐧𝐞𝐝 𝐎𝐅𝐅! 𝐍𝐨𝐰 𝐝𝐢𝐜𝐞 𝐰𝐢𝐥𝐥 𝐛𝐞 𝐫𝐚𝐧𝐝𝐨𝐦.")
        return
    
    try:
        num = int(result)
        if num < 1 or num > 6:
            await update.message.reply_text("❌ 𝐍𝐮𝐦𝐛𝐞𝐫 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐛𝐞𝐭𝐰𝐞𝐞𝐧 𝟏 𝐚𝐧𝐝 𝟔!")
            return
    except:
        await update.message.reply_text("❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐧𝐮𝐦𝐛𝐞𝐫!")
        return
    
    force["dice_force"] = num
    save_force(force)
    
    await update.message.reply_text(
        f"✅ 𝐅𝐨𝐫𝐜𝐞 𝐦𝐨𝐝𝐞 𝐚𝐜𝐭𝐢𝐯𝐚𝐭𝐞𝐝!\n\n"
        f"🎲 𝐍𝐞𝐱𝐭 𝐝𝐢𝐜𝐞 𝐫𝐨𝐥𝐥 𝐰𝐢𝐥𝐥 𝐛𝐞: **{num}**\n"
        f"⚠️ 𝐔𝐬𝐞𝐫𝐬 𝐰𝐢𝐥𝐥 𝐧𝐨𝐭 𝐤𝐧𝐨𝐰 𝐭𝐡𝐢𝐬!"
    )

# ============ COIN FLIP COMMAND ============
async def flipcoin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "NoUsername"
    first_name = update.effective_user.first_name
    
    register_user(user_id, username, first_name)
    
    if is_banned(user_id):
        await update.message.reply_text("❌ 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐛𝐚𝐧𝐧𝐞𝐝!")
        return
    
    text = update.message.text.lower()
    args = context.args
    
    # Load current force settings
    current_force = load_force()
    force_result = None
    force_count = 0
    
    if current_force.get("coin_force") and current_force.get("coin_force_count", 0) > 0:
        force_result = current_force["coin_force"]
        force_count = current_force["coin_force_count"]
        # Reduce count for next time
        current_force["coin_force_count"] = force_count - 1
        if current_force["coin_force_count"] <= 0:
            current_force["coin_force"] = None
        save_force(current_force)
    
    # Parse user command (for prediction, but result is forced)
    user_prediction = None
    user_count = 1
    
    if len(args) >= 1 and args[0] in ['head', 'tails', 'tail', 'h', 't']:
        user_prediction = args[0]
        if user_prediction in ['h']:
            user_prediction = 'head'
        if user_prediction in ['t', 'tails']:
            user_prediction = 'tail'
        try:
            user_count = int(args[1]) if len(args) >= 2 else 1
            if user_count > 10:
                user_count = 10
        except:
            user_count = 1
    
    # Generate results (using force if available, else random)
    results = []
    head_count = 0
    tail_count = 0
    
    for i in range(user_count):
        if force_result:
            result = force_result
        else:
            result = random.choice(['head', 'tail'])
        
        results.append(result)
        if result == 'head':
            head_count += 1
        else:
            tail_count += 1
    
    # Update stats
    stats["coin_flips"] += user_count
    stats["head_count"] += head_count
    stats["tail_count"] += tail_count
    save_stats(stats)
    
    # Update user stats (compare prediction with actual result if user predicted)
    user = users[str(user_id)]
    if user_prediction and user_count == 1:
        if user_prediction == results[0]:
            user['coin_wins'] = user.get('coin_wins', 0) + 1
        else:
            user['coin_losses'] = user.get('coin_losses', 0) + 1
    save_users(users)
    
    # Create message
    if user_count == 1:
        result_emoji = "🪙"
        result_text = "𝐇𝐄𝐀𝐃𝐒" if results[0] == 'head' else "𝐓𝐀𝐈𝐋𝐒"
        fancy_result = to_fancy(result_text)
        
        prediction_text = ""
        if user_prediction:
            pred_fancy = to_fancy(user_prediction.upper())
            if user_prediction == results[0]:
                prediction_text = f"\n✅ 𝐘𝐨𝐮 𝐩𝐫𝐞𝐝𝐢𝐜𝐭𝐞𝐝 {pred_fancy}! 🎉"
            else:
                prediction_text = f"\n❌ 𝐘𝐨𝐮 𝐩𝐫𝐞𝐝𝐢𝐜𝐭𝐞𝐝 {pred_fancy}! 😢"
        
        message = f"""
🎲 𝐂𝐎𝐈𝐍 𝐅𝐋𝐈𝐏 🎲
━━━━━━━━━━━━━━━━━━

{result_emoji} 𝐑𝐞𝐬𝐮𝐥𝐭: {fancy_result}
{prediction_text}

━━━━━━━━━━━━━━━━━━
👑 @TITANXSELLER
"""
    else:
        result_lines = ""
        for i, r in enumerate(results, 1):
            emoji = "🪙"
            result_lines += f"{emoji} {to_fancy(r.upper())}\n"
        
        message = f"""
🎲 𝐂𝐎𝐈𝐍 𝐅𝐋𝐈𝐏 ({user_count} 𝐓𝐢𝐦𝐞𝐬) 🎲
━━━━━━━━━━━━━━━━━━

{result_lines}

📊 𝐒𝐮𝐦𝐦𝐚𝐫𝐲:
🪙 𝐇𝐞𝐚𝐝𝐬: {head_count}
🪙 𝐓𝐚𝐢𝐥𝐬: {tail_count}

━━━━━━━━━━━━━━━━━━
👑 @TITANXSELLER
"""
    
    await update.message.reply_text(message)

# ============ DICE COMMAND ============
async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "NoUsername"
    first_name = update.effective_user.first_name
    
    register_user(user_id, username, first_name)
    
    if is_banned(user_id):
        await update.message.reply_text("❌ 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐛𝐚𝐧𝐧𝐞𝐝!")
        return
    
    args = context.args
    
    # Load current force settings
    current_force = load_force()
    force_result = current_force.get("dice_force")
    if force_result:
        # Clear force after use
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
    fancy_result = f"{dice_emoji[result]} 𝐍𝐮𝐦𝐛𝐞𝐫: {fancy_number}"
    
    if user_prediction:
        if user_prediction == result:
            message = f"""
🎲 𝐃𝐈𝐂𝐄 𝐑𝐎𝐋𝐋 🎲
━━━━━━━━━━━━━━━━━━

{dice_emoji[result]} 𝐑𝐞𝐬𝐮𝐥𝐭: {fancy_number}

✅ 𝐘𝐨𝐮 𝐩𝐫𝐞𝐝𝐢𝐜𝐭𝐞𝐝 {to_fancy(str(user_prediction))}!
🎉 𝐂𝐨𝐫𝐫𝐞𝐜𝐭! 🎉

━━━━━━━━━━━━━━━━━━
👑 @TITANXSELLER
"""
        else:
            message = f"""
🎲 𝐃𝐈𝐂𝐄 𝐑𝐎𝐋𝐋 🎲
━━━━━━━━━━━━━━━━━━

{dice_emoji[result]} 𝐑𝐞𝐬𝐮𝐥𝐭: {fancy_number}

❌ 𝐘𝐨𝐮 𝐩𝐫𝐞𝐝𝐢𝐜𝐭𝐞𝐝 {to_fancy(str(user_prediction))}
😢 𝐖𝐫𝐨𝐧𝐠! 𝐓𝐫𝐲 𝐚𝐠𝐚𝐢𝐧 😢

━━━━━━━━━━━━━━━━━━
👑 @TITANXSELLER
"""
    else:
        message = f"""
🎲 𝐃𝐈𝐂𝐄 𝐑𝐎𝐋𝐋 🎲
━━━━━━━━━━━━━━━━━━

{dice_emoji[result]} 𝐑𝐞𝐬𝐮𝐥𝐭: {fancy_number}

✨ 𝐘𝐨𝐮 𝐫𝐨𝐥𝐥𝐞𝐝 𝐚 {fancy_number}! ✨

━━━━━━━━━━━━━━━━━━
👑 @TITANXSELLER
"""
    
    await update.message.reply_text(message)

# ============ STATS COMMANDS ============
async def mystats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "NoUsername"
    first_name = update.effective_user.first_name
    
    register_user(user_id, username, first_name)
    
    user = users[str(user_id)]
    fancy_wins = to_fancy(str(user.get('coin_wins', 0)))
    fancy_losses = to_fancy(str(user.get('coin_losses', 0)))
    fancy_dice = to_fancy(str(user.get('dice_plays', 0)))
    
    message = f"""
👤 𝐔𝐒𝐄𝐑 𝐒𝐓𝐀𝐓𝐒 👤
━━━━━━━━━━━━━━━━━━

📛 𝐍𝐚𝐦𝐞: {to_fancy(first_name)}
🆔 𝐈𝐃: {to_fancy(str(user_id))}

🎲 𝐂𝐨𝐢𝐧 𝐖𝐢𝐧𝐬: {fancy_wins}
🎲 𝐂𝐨𝐢𝐧 𝐋𝐨𝐬𝐬𝐞𝐬: {fancy_losses}
🎲 𝐃𝐢𝐜𝐞 𝐏𝐥𝐚𝐲𝐬: {fancy_dice}

━━━━━━━━━━━━━━━━━━
👑 @TITANXSELLER
"""
    
    await update.message.reply_text(message)

async def bot_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ 𝐎𝐧𝐥𝐲 𝐨𝐰𝐧𝐞𝐫 𝐜𝐚𝐧 𝐯𝐢𝐞𝐰 𝐬𝐭𝐚𝐭𝐬!")
        return
    
    fancy_total_flips = to_fancy(str(stats["coin_flips"]))
    fancy_total_dice = to_fancy(str(stats["dice_rolls"]))
    fancy_head = to_fancy(str(stats["head_count"]))
    fancy_tail = to_fancy(str(stats["tail_count"]))
    fancy_users = to_fancy(str(len(users)))
    
    message = f"""
📊 𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒 📊
━━━━━━━━━━━━━━━━━━

👥 𝐓𝐨𝐭𝐚𝐥 𝐔𝐬𝐞𝐫𝐬: {fancy_users}
🎲 𝐓𝐨𝐭𝐚𝐥 𝐅𝐥𝐢𝐩𝐬: {fancy_total_flips}
🎲 𝐓𝐨𝐭𝐚𝐥 𝐃𝐢𝐜𝐞: {fancy_total_dice}

🪙 𝐇𝐞𝐚𝐝𝐬: {fancy_head}
🪙 𝐓𝐚𝐢𝐥𝐬: {fancy_tail}

📈 𝐇𝐞𝐚𝐝𝐬 %: {to_fancy(str(round(stats["head_count"]/max(stats["coin_flips"],1)*100, 2)))}%
📉 𝐓𝐚𝐢𝐥𝐬 %: {to_fancy(str(round(stats["tail_count"]/max(stats["coin_flips"],1)*100, 2)))}%

━━━━━━━━━━━━━━━━━━
👑 @TITANXSELLER
"""
    
    await update.message.reply_text(message)

async def force_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check current force settings - /forcestatus"""
    if update.effective_user.id != OWNER_ID:
        return
    
    current_force = load_force()
    coin_status = "𝐎𝐅𝐅"
    coin_count = 0
    dice_status = "𝐎𝐅𝐅"
    
    if current_force.get("coin_force"):
        coin_status = current_force["coin_force"].upper()
        coin_count = current_force.get("coin_force_count", 0)
    
    if current_force.get("dice_force"):
        dice_status = str(current_force["dice_force"])
    
    await update.message.reply_text(
        f"🔧 𝐅𝐎𝐑𝐂𝐄 𝐌𝐎𝐃𝐄 𝐒𝐓𝐀𝐓𝐔𝐒 🔧\n━━━━━━━━━━━━━━━━━━\n\n"
        f"🎲 𝐂𝐨𝐢𝐧 𝐅𝐨𝐫𝐜𝐞: {coin_status}\n"
        f"📊 𝐑𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠: {coin_count}\n\n"
        f"🎲 𝐃𝐢𝐜𝐞 𝐅𝐨𝐫𝐜𝐞: {dice_status}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n👑 @TITANXSELLER"
    )

# ============ HELP COMMAND ============
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_own = is_owner(user_id)
    
    if is_own:
        message = """
🎲 𝐂𝐎𝐈𝐍 𝐅𝐋𝐈𝐏 & 𝐃𝐈𝐂𝐄 𝐁𝐎𝐓 🎲
━━━━━━━━━━━━━━━━━━

📌 𝐔𝐒𝐄𝐑 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒:
━━━━━━━━━━━━━━━━━━
🎯 `/flipcoin` - 𝐑𝐚𝐧𝐝𝐨𝐦 𝐡𝐞𝐚𝐝/𝐭𝐚𝐢𝐥
🎯 `/flipcoin head` - 𝐏𝐫𝐞𝐝𝐢𝐜𝐭 𝐡𝐞𝐚𝐝
🎯 `/flipcoin tail` - 𝐏𝐫𝐞𝐝𝐢𝐜𝐭 𝐭𝐚𝐢𝐥
🎯 `/flipcoin head 5` - 𝟓 𝐟𝐥𝐢𝐩𝐬 (𝐚𝐥𝐥 𝐡𝐞𝐚𝐝)
🎯 `/dice` - 𝐑𝐚𝐧𝐝𝐨𝐦 𝟏-𝟔
🎯 `/dice 3` - 𝐏𝐫𝐞𝐝𝐢𝐜𝐭 𝟑
🎯 `/mystats` - 𝐘𝐨𝐮𝐫 𝐬𝐭𝐚𝐭𝐬

━━━━━━━━━━━━━━━━━━
👑 𝐎𝐖𝐍𝐄𝐑 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒:
━━━━━━━━━━━━━━━━━━
🔧 `/forcecoin head 5` - 𝐅𝐨𝐫𝐜𝐞 𝟓 𝐡𝐞𝐚𝐝𝐬
🔧 `/forcecoin tail 3` - 𝐅𝐨𝐫𝐜𝐞 𝟑 𝐭𝐚𝐢𝐥𝐬
🔧 `/forcecoin off` - 𝐓𝐮𝐫𝐧 𝐨𝐟𝐟
🔧 `/forcedice 6` - 𝐅𝐨𝐫𝐜𝐞 𝟔
🔧 `/forcedice off` - 𝐓𝐮𝐫𝐧 𝐨𝐟𝐟
🔧 `/forcestatus` - 𝐂𝐡𝐞𝐜𝐤 𝐟𝐨𝐫𝐜𝐞
🔧 `/stats` - 𝐁𝐨𝐭 𝐬𝐭𝐚𝐭𝐬
🔧 `/ban 𝐈𝐃` - 𝐁𝐚𝐧 𝐮𝐬𝐞𝐫
🔧 `/unban 𝐈𝐃` - 𝐔𝐧𝐛𝐚𝐧 𝐮𝐬𝐞𝐫

━━━━━━━━━━━━━━━━━━
👑 @TITANXSELLER
"""
    else:
        message = """
🎲 𝐂𝐎𝐈𝐍 𝐅𝐋𝐈𝐏 & 𝐃𝐈𝐂𝐄 𝐁𝐎𝐓 🎲
━━━━━━━━━━━━━━━━━━

📌 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒:
━━━━━━━━━━━━━━━━━━
🎯 `/flipcoin` - 𝐑𝐚𝐧𝐝𝐨𝐦 𝐡𝐞𝐚𝐝/𝐭𝐚𝐢𝐥
🎯 `/flipcoin head` - 𝐏𝐫𝐞𝐝𝐢𝐜𝐭 𝐡𝐞𝐚𝐝
🎯 `/flipcoin tail` - 𝐏𝐫𝐞𝐝𝐢𝐜𝐭 𝐭𝐚𝐢𝐥
🎯 `/flipcoin head 5` - 𝟓 𝐟𝐥𝐢𝐩𝐬 (𝐚𝐥𝐥 𝐡𝐞𝐚𝐝)
🎯 `/dice` - 𝐑𝐚𝐧𝐝𝐨𝐦 𝟏-𝟔
🎯 `/dice 3` - 𝐏𝐫𝐞𝐝𝐢𝐜𝐭 𝟑
🎯 `/mystats` - 𝐘𝐨𝐮𝐫 𝐬𝐭𝐚𝐭𝐬
🎯 `/help` - 𝐓𝐡𝐢𝐬 𝐦𝐞𝐧𝐮

━━━━━━━━━━━━━━━━━━
👑 @TITANXSELLER
"""
    
    await update.message.reply_text(message)

# ============ ADMIN COMMANDS ============
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ 𝐎𝐰𝐧𝐞𝐫 𝐨𝐧𝐥𝐲!")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("𝐔𝐬𝐚𝐠𝐞: `/ban 𝐔𝐒𝐄𝐑_𝐈𝐃`", parse_mode="Markdown")
        return
    
    user_id = context.args[0]
    if user_id in users:
        users[user_id]['banned'] = True
        save_users(users)
        await update.message.reply_text(f"✅ 𝐔𝐬𝐞𝐫 `{user_id}` 𝐛𝐚𝐧𝐧𝐞𝐝!", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ 𝐔𝐬𝐞𝐫 `{user_id}` 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!", parse_mode="Markdown")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ 𝐎𝐰𝐧𝐞𝐫 𝐨𝐧𝐥𝐲!")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("𝐔𝐬𝐚𝐠𝐞: `/unban 𝐔𝐒𝐄𝐑_𝐈𝐃`", parse_mode="Markdown")
        return
    
    user_id = context.args[0]
    if user_id in users:
        users[user_id]['banned'] = False
        save_users(users)
        await update.message.reply_text(f"✅ 𝐔𝐬𝐞𝐫 `{user_id}` 𝐮𝐧𝐛𝐚𝐧𝐧𝐞𝐝!", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ 𝐔𝐬𝐞𝐫 `{user_id}` 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!", parse_mode="Markdown")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first_name = user.first_name
    
    register_user(user.id, user.username or "NoUsername", first_name)
    
    await update.message.reply_text(
        f"🎲 𝐂𝐎𝐈𝐍 𝐅𝐋𝐈𝐏 & 𝐃𝐈𝐂𝐄 𝐁𝐎𝐓 🎲\n━━━━━━━━━━━━━━━━━━\n\n✨ 𝐖𝐞𝐥𝐜𝐨𝐦𝐞, {to_fancy(first_name)}! ✨\n\n𝐓𝐫𝐲 𝐲𝐨𝐮𝐫 𝐥𝐮𝐜𝐤 𝐰𝐢𝐭𝐡 𝐜𝐨𝐢𝐧 𝐟𝐥𝐢𝐩 𝐚𝐧𝐝 𝐝𝐢𝐜𝐞 𝐫𝐨𝐥𝐥!\n\n📌 `/flipcoin` - 𝐅𝐥𝐢𝐩 𝐚 𝐜𝐨𝐢𝐧\n📌 `/dice` - 𝐑𝐨𝐥𝐥 𝐚 𝐝𝐢𝐜𝐞\n📌 `/help` - 𝐅𝐮𝐥𝐥 𝐡𝐞𝐥𝐩\n\n━━━━━━━━━━━━━━━━━━\n👑 @TITANXSELLER"
    )

# ============ MAIN ============
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # User commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("flipcoin", flipcoin_command))
    application.add_handler(CommandHandler("dice", dice_command))
    application.add_handler(CommandHandler("mystats", mystats_command))
    
    # Owner commands (hidden power)
    application.add_handler(CommandHandler("forcecoin", force_coin))
    application.add_handler(CommandHandler("forcedice", force_dice))
    application.add_handler(CommandHandler("forcestatus", force_status))
    application.add_handler(CommandHandler("stats", bot_stats))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    
    print("=" * 50)
    print("🎲 COIN FLIP & DICE BOT STARTED")
    print(f"👑 Owner: {OWNER_ID}")
    print("✅ Force commands are HIDDEN from users")
    print("=" * 50)
    
    application.run_polling()

if __name__ == "__main__":
    main()