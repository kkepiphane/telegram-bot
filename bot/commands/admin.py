from telegram import Update
from telegram.ext import ContextTypes
import os
from bot.database import get_db_connection

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != os.getenv("ADMIN_ID"):
        await update.message.reply_text("Accès refusé")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM groups")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM groups WHERE is_active = 1")
    active = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports")
    reports = cursor.fetchone()[0]

    conn.close()

    await update.message.reply_text(
        f"📊 Statistiques :\n"
        f"- Groupes totaux : {total}\n"
        f"- Groupes actifs : {active}\n"
        f"- Signalements : {reports}"
    )