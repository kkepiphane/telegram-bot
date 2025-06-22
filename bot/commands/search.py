from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database import get_db_connection


async def search_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    print(f"Reçu callback_data: {query.data}")  # Log de débogage
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("FR", callback_data="search_fr"),
         InlineKeyboardButton("EN", callback_data="search_en")],
        [InlineKeyboardButton("Tous", callback_data="search_all")]
    ]

    try:
        await query.edit_message_text(
            "Filtrer par langue :",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        print(f"Erreur dans search_groups: {e}")


async def show_groups(update: Update, context: ContextTypes.DEFAULT_TYPE, language=None):
    query = update.callback_query
    await query.answer()  # Important pour éviter l'icône de chargement

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
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

        if not groups:
            await query.edit_message_text("Aucun groupe trouvé 😢")
            return

        response = "🔝 Top Groupes:\n\n" if not language else f"🔝 Top Groupes ({language}):\n\n"
        for idx, (name, link) in enumerate(groups, 1):
            # Nettoyer le lien si nécessaire
            if not link.startswith('https://'):
                link = f'https://{link}'
            response += f"{idx}. [{name}]({link})\n"

        await query.edit_message_text(
            text=response,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"Erreur lors de la recherche: {e}")
        await query.edit_message_text("Erreur lors de la recherche 😢")
    finally:
        conn.close()
