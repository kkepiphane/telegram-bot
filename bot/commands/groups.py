import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import Config
from bot.utils import is_valid_group
from bot.database import get_db_connection
from datetime import datetime

async def start_add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Entrez le nom du groupe :\n"
        "(Annuler avec /cancel)"
    )
    return Config.GROUP_NAME

async def process_group_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['group_name'] = update.message.text
    await update.message.reply_text(
        "Maintenant, envoyez le lien d'invitation :\n"
        "(Doit commencer par 'https://t.me/' ou 't.me/')"
    )
    return Config.GROUP_LINK

async def process_group_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text
    if not (link.startswith('t.me/') or link.startswith('https://t.me/')):
        await update.message.reply_text("Format de lien invalide !")
        return Config.GROUP_LINK

    if not await is_valid_group(link, context):
        await update.message.reply_text("Lien invalide ou groupe inaccessible !")
        return Config.GROUP_LINK

    context.user_data['group_link'] = link

    keyboard = [
        [InlineKeyboardButton("Français", callback_data="lang_fr")],
        [InlineKeyboardButton("English", callback_data="lang_en")]
    ]

    await update.message.reply_text(
        "Sélectionnez la langue principale :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return Config.GROUP_LANG

async def save_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    language = 'FR' if query.data == 'lang_fr' else 'EN'

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO groups (name, link, language, date_added)
            VALUES (?, ?, ?, ?)
        ''', (
            context.user_data['group_name'],
            context.user_data['group_link'],
            language,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        await query.edit_message_text("Groupe soumis pour approbation ! ✅")
    except sqlite3.IntegrityError:
        await query.edit_message_text("Ce groupe est déjà dans la base de données !")
    finally:
        conn.close()

    return ConversationHandler.END