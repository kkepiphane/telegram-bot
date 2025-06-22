from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database import get_db_connection
from config import Config
from telegram.ext import ConversationHandler

async def start_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM groups WHERE is_active = 1 LIMIT 20")
    groups = cursor.fetchall()
    conn.close()

    if not groups:
        await query.edit_message_text("Aucun groupe à signaler pour le moment")
        return Config.REPORT_GROUP

    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"report_{id}")]
        for id, name in groups
    ]

    await query.edit_message_text(
        "Sélectionnez un groupe à signaler :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return Config.REPORT_GROUP


async def process_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    group_id = int(query.data.split('_')[1])
    context.user_data['report_group_id'] = group_id

    await query.edit_message_text(
        "Décrivez le problème (lien mort, contenu inapproprié...) :\n"
        "(Annuler avec /cancel)"
    )
    return Config.REPORT_GROUP


async def save_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reason = update.message.text
    group_id = context.user_data['report_group_id']
    user_id = update.message.from_user.id

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO reports (group_id, reporter_id, reason)
        VALUES (?, ?, ?)
    ''', (group_id, user_id, reason))

    cursor.execute('''
        UPDATE groups 
        SET reported_count = reported_count + 1
        WHERE id = ?
    ''', (group_id,))

    cursor.execute('''
        UPDATE groups 
        SET is_active = 0
        WHERE id = ? AND reported_count >= 3
    ''', (group_id,))

    conn.commit()
    conn.close()

    await update.message.reply_text("Merci pour votre signalement ! Nous allons vérifier.")
    return ConversationHandler.END
