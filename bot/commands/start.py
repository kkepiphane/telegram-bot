from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 Rechercher", callback_data="search")],
        [InlineKeyboardButton("📌 Proposer un groupe", callback_data="add_group")],
        [InlineKeyboardButton("⚠️ Signaler un groupe", callback_data="report")]
    ]
    await update.message.reply_text(
        "Bienvenue dans Otaku Finder 2.0 !",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )