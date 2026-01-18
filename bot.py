import logging
import sqlite3
import random
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================
TOKEN = "8289179943:AAGwym_czUhsWPLmWsJg5BwSA4SxQfxXOZg"
ADMIN_ID = 8308835896  # This is your ID

DB_NAME = "signalmaster.db"
MAX_MARTINGALE_LEVEL = 6
FREE_SIGNALS_LIMIT = 20

# FULL OTC PAIR LIST
PAIRS = [
    "BTC/USD OTC", "ETH/USD OTC", "EUR/USD OTC", "EUR/GBP OTC", "USD/CHF OTC", "EUR/JPY OTC",
    "GBP/USD OTC", "GBP/JPY OTC", "AUD/CAD OTC", "USD/ZAR OTC", "USD/SGD OTC", "USD/HKD OTC",
    "USD/INR OTC", "AUD/USD OTC", "USD/CAD OTC", "AUD/JPY OTC", "GBP/CAD OTC", "GBP/CHF OTC",
    "GBP/AUD OTC", "EUR/CAD OTC", "CHF/JPY OTC", "CAD/CHF OTC", "EUR/AUD OTC", "EUR/NZD OTC",
    "USD/NOK OTC", "USD/SEK OTC", "USD/TRY OTC", "USD/PLN OTC", "AUD/CHF OTC", "AUD/NZD OTC",
    "EUR/CHF OTC", "GBP/NZD OTC", "CAD/JPY OTC", "NZD/CAD OTC", "NZD/JPY OTC", "EUR/THB OTC",
    "USD/THB OTC", "JPY/THB OTC", "CHF/NOK OTC", "NOK/JPY OTC", "USD/BRL OTC", "USD/COP OTC",
    "PEN/USD OTC", "ONDO OTC", "SHIB/USD OTC", "SNAP INC OTC", "USD/MXN OTC", "RAYDIUM OTC",
    "SUI OTC", "HBAR OTC", "RENDER OTC", "GOLD", "AMAZON OTC", "GOOGLE OTC", "TESLA OTC",
    "META OTC", "BONK OTC", "PEPE OTC", "IOTA OTC"
]

TIMEFRAMES = ["1m", "3m", "5m", "15m"]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ==============================================================================
# 2. DATABASE LAYER
# ==============================================================================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            free_signals INTEGER DEFAULT 20,
            martingale_level INTEGER DEFAULT 0,
            max_martingale_reached INTEGER DEFAULT 0,
            subscription_status INTEGER DEFAULT 0,
            active_chain INTEGER DEFAULT 0,
            last_pair TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    if not user:
        c.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = c.fetchone()
    conn.close()
    return user

def update_user_stat(user_id, **kwargs):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    kwargs['last_active'] = datetime.now()
    set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [user_id]
    c.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", values)
    conn.commit()
    conn.close()

# ==============================================================================
# 3. CORE SERVICES
# ==============================================================================
def generate_market_signal(last_pair=None):
    available_pairs = [p for p in PAIRS if p != last_pair]
    pair = random.choice(available_pairs if available_pairs else PAIRS)
    timeframe = random.choice(TIMEFRAMES)
    
    # Smart Delay: 2 to 7 minutes in future
    now = datetime.now()
    delay_minutes = random.randint(2, 7)
    future_time = now + timedelta(minutes=delay_minutes)
    open_time_str = future_time.strftime("%H:%M")
    
    return {"pair": pair, "time": open_time_str, "timeframe": timeframe}

# ==============================================================================
# 4. BOT HANDLERS & PAYMENT
# ==============================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    intro_text = (
        "🤖 **SignalMaster Bot — Professional Trading Signals**\n\n"
        "I generate deeply analyzed signals using chart memory and top-tier indicator mastery.\n\n"
        "📌 **Strategy Rule:**\n"
        "Follow the signals strictly. Potential to earn significant returns when applied correctly.\n\n"
        "⚠️ **Martingale Safety Rule:**\n"
        "Maximum martingale level is 6.\n"
        "Safety limit = Capital ÷ 63.\n"
        f"*(Example: $63 Capital = Start Stake $1)*\n\n"
        f"📌 **Free Signals:** {user['free_signals']} remaining.\n"
    )
    keyboard = [
        [InlineKeyboardButton("▶️ START TRADING", callback_data='action_start')],
        [InlineKeyboardButton("📊 CHECK STATISTICS", callback_data='action_stats')],
        [InlineKeyboardButton("💳 SUBSCRIBE", callback_data='action_sub')]
    ]
    await update.message.reply_text(intro_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    # ⚠️ EDIT THESE DETAILS BEFORE LAUNCH ⚠️
    USDT_ADDRESS = "T9xxxxxxxxxxxxxxxxxxxxxxxxxxxx"  
    BANK_NAME = "OPAY"                            
    ACCOUNT_NUMBER = "8123456789"                 
    ACCOUNT_NAME = "YOUR NAME"               
    PRICE_NGN = "85,000"
    ADMIN_USERNAME = "YourTelegramUsername" # Put your username here (without @)

    msg = (
        "💳 **PREMIUM SUBSCRIPTION**\n\n"
        "Unlock unlimited signals and maximize your profit potential.\n"
        f"**Price:** $50 / ₦{PRICE_NGN} (Lifetime)\n\n"
        
        "━━━━━━━━━━━━━━━━━━\n"
        "**OPTION 1: CRYPTO (USDT TRC20)**\n"
        "Tap to copy address:\n"
        f"`{USDT_ADDRESS}`\n\n"
        
        "━━━━━━━━━━━━━━━━━━\n"
        "**OPTION 2: BANK TRANSFER (NGN)**\n"
        f"🏦 Bank: **{BANK_NAME}**\n"
        f"🔢 Acct: `{ACCOUNT_NUMBER}`\n"
        f"👤 Name: **{ACCOUNT_NAME}**\n\n"
        
        "━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ **VERIFICATION:**\n"
        f"After payment, send your User ID `{user_id}` and a screenshot of the receipt to the Admin."
    )
    
    keyboard = [[InlineKeyboardButton("📩 SEND PROOF TO ADMIN", url=f"https://t.me/{ADMIN_USERNAME}")]]
    await query.message.reply_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def send_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user = get_user(user_id)

    # Check Subscription
    if user['free_signals'] <= 0 and not user['subscription_status']:
        await query.message.reply_text(
            "⛔ **Free Signals Depleted**\n\n"
            "You have used all your free signals.\n"
            "Please subscribe to continue trading.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 SUBSCRIBE NOW", callback_data='action_sub')]])
        )
        return

    # Check Martingale Safety
    if user['martingale_level'] >= MAX_MARTINGALE_LEVEL:
        update_user_stat(user_id, martingale_level=0, active_chain=0)
        await query.message.reply_text(
            "⚠️ **Safety Limit Reached (Level 6)**\n\n"
            "You have reached the maximum martingale level.\n"
            "The chain has been reset to protect your capital.\n\n"
            "Generating fresh signal...",
            parse_mode='Markdown'
        )
        await asyncio.sleep(2)
        user = get_user(user_id)

    # Generate Signal
    signal_data = generate_market_signal(last_pair=user['last_pair'])
    update_user_stat(user_id, last_pair=signal_data['pair'])

    msg = (
        "📊 **SIGNAL GENERATED**\n\n"
        f"**Pair:** {signal_data['pair']}\n"
        f"**Open Time:** {signal_data['time']}\n"
        f"**Candle Timeframe:** {signal_data['timeframe']}\n\n"
        f"⚡ *Martingale Level: {user['martingale_level']}*\n"
        "Confirm result:"
    )
    keyboard = [[InlineKeyboardButton("✅ WIN", callback_data='result_win'), InlineKeyboardButton("❌ LOSS", callback_data='result_loss')]]
    await query.message.reply_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    user = get_user(user_id)

    if data == 'result_win':
        new_free = user['free_signals'] - 1
        update_user_stat(user_id, martingale_level=0, active_chain=0, free_signals=new_free)
        await query.message.edit_text(
            f"✅ **WIN CONFIRMED**\n\nMartingale reset to Level 0.\nSignals remaining: {new_free if not user['subscription_status'] else 'Unlimited'}\nGenerating new signal...",
            parse_mode='Markdown'
        )
        await asyncio.sleep(1.5)
        await send_signal(update, context)

    elif data == 'result_loss':
        new_level = user['martingale_level'] + 1
        new_max = max(user['max_martingale_reached'], new_level)
        update_user_stat(user_id, martingale_level=new_level, active_chain=1, max_martingale_reached=new_max)
        await query.message.edit_text(
            f"❌ **LOSS CONFIRMED**\n\nMartingale increased to Level {new_level}.\nAnalyzing next pair to recover...",
            parse_mode='Markdown'
        )
        await asyncio.sleep(1.5)
        await send_signal(update, context)

async def check_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = get_user(user_id)
    stats_msg = (
        "📊 **Your Statistics**\n\n"
        f"🆔 User ID: `{user_id}`\n"
        f"⚡ Martingale Level: **{user['martingale_level']}**\n"
        f"📈 Max Level: **{user['max_martingale_reached']}**\n"
        f"🎟️ Free Signals: **{user['free_signals']}**\n"
        f"💎 Status: **{'PREMIUM' if user['subscription_status'] else 'FREE'}**"
    )
    keyboard = [[InlineKeyboardButton("▶️ GENERATE SIGNAL", callback_data='action_start')]]
    await query.message.reply_text(stats_msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return 

    try:
        target_id = int(context.args[0])
        update_user_stat(target_id, subscription_status=1)
        await update.message.reply_text(f"✅ User {target_id} is now PREMIUM.")
        try:
            await context.bot.send_message(chat_id=target_id, text="🎉 **Payment Received!**\n\nYour Premium Subscription is now ACTIVE.\nYou have unlimited signals.")
        except:
            await update.message.reply_text(f"⚠️ User {target_id} upgraded, but couldn't send DM.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Usage: /approve <user_id>")

# ==============================================================================
# 5. MAIN EXECUTION
# ==============================================================================
if __name__ == '__main__':
    init_db()
    print("Database initialized.")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("approve", admin_approve)) 
    app.add_handler(CallbackQueryHandler(send_signal, pattern='^action_start$'))
    app.add_handler(CallbackQueryHandler(check_stats, pattern='^action_stats$'))
    app.add_handler(CallbackQueryHandler(subscribe, pattern='^action_sub$'))
    app.add_handler(CallbackQueryHandler(handle_result, pattern='^result_'))

    print("Bot is running...")
    app.run_polling()
