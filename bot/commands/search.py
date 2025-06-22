from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database import get_db_connection

async def search_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("FR", callback_data="search_fr"),
         InlineKeyboardButton("EN", callback_data="search_en")],
        [InlineKeyboardButton("Tous", callback_data="search_all")]
    ]

    await query.edit_message_text(
        "Filtrer par langue :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_groups(update: Update, context: ContextTypes.DEFAULT_TYPE, language=None):
    query = update.callback_query
    await query.answer()

    conn = get_db_connection()
    cursor = conn.cursor()

    if language:
        cursor.execute('''
            SELECT name, link FROM groups 
            WHERE language = ? AND is_active = 1
            ORDER BY votes DESC LIMIT 10
        ''', (language,))
    else:
        cursor.execute('''
            SELECT name, link FROM groups 
            WHERE is_active = 1
            ORDER BY votes DESC LIMIT 10
        ''')

    groups = cursor.fetchall()
    conn.close()

    if not groups:
        await query.edit_message_text("Aucun groupe trouvé 😢")
        return

    response = "🔝 Top Groupes:\n\n" if not language else f"🔝 Top Groupes ({language}):\n\n"
    for idx, (name, link) in enumerate(groups, 1):
        response += f"{idx}. [{name}]({link})\n"

    await query.edit_message_text(response, parse_mode="Markdown")