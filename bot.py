from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from telegram.constants import ChatAction
import sqlite3
from dotenv import load_dotenv
import os
from datetime import datetime

# Configuration initiale
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DB_NAME = "otaku_groups.db"

# États pour la conversation
GROUP_NAME, GROUP_LINK, GROUP_LANG = range(3)
REPORT_GROUP = 1

# Initialisation BD améliorée
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            link TEXT UNIQUE NOT NULL,
            language TEXT,
            category TEXT,
            votes INTEGER DEFAULT 0,
            date_added TEXT DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            reported_count INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY,
            group_id INTEGER,
            reporter_id INTEGER,
            reason TEXT,
            date_reported TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(group_id) REFERENCES groups(id)
        )
    ''')
    conn.commit()
    conn.close()

# Vérification des liens
async def is_valid_group(link: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        await context.bot.send_chat_action(chat_id=link, action=ChatAction.TYPING)
        return True
    except Exception as e:
        print(f"Lien invalide: {e}")
        return False

# Commandes de base
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

# Recherche améliorée
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
    
    conn = sqlite3.connect(DB_NAME)
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

# Système d'ajout avec modération
async def start_add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Entrez le nom du groupe :\n"
        "(Annuler avec /cancel)"
    )
    return GROUP_NAME

async def process_group_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['group_name'] = update.message.text
    await update.message.reply_text(
        "Maintenant, envoyez le lien d'invitation :\n"
        "(Doit commencer par 'https://t.me/')"
    )
    return GROUP_LINK

async def process_group_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text
    if not link.startswith('https://t.me/'):
        await update.message.reply_text("Format de lien invalide !")
        return GROUP_LINK
    
    if not await is_valid_group(link, context):
        await update.message.reply_text("Lien invalide ou groupe inaccessible !")
        return GROUP_LINK
    
    context.user_data['group_link'] = link
    
    keyboard = [
        [InlineKeyboardButton("Français", callback_data="lang_fr")],
        [InlineKeyboardButton("English", callback_data="lang_en")]
    ]
    
    await update.message.reply_text(
        "Sélectionnez la langue principale :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return GROUP_LANG

async def save_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    language = 'FR' if query.data == 'lang_fr' else 'EN'
    
    conn = sqlite3.connect(DB_NAME)
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

# Système de signalement
async def start_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM groups WHERE is_active = 1 LIMIT 20")
    groups = cursor.fetchall()
    conn.close()
    
    if not groups:
        await query.edit_message_text("Aucun groupe à signaler pour le moment")
        return
    
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"report_{id}")]
        for id, name in groups
    ]
    
    await query.edit_message_text(
        "Sélectionnez un groupe à signaler :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return REPORT_GROUP

async def process_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    group_id = int(query.data.split('_')[1])
    context.user_data['report_group_id'] = group_id
    
    await query.edit_message_text(
        "Décrivez le problème (lien mort, contenu inapproprié...) :\n"
        "(Annuler avec /cancel)"
    )
    return REPORT_GROUP

async def save_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reason = update.message.text
    group_id = context.user_data['report_group_id']
    user_id = update.message.from_user.id
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Enregistrer le signalement
    cursor.execute('''
        INSERT INTO reports (group_id, reporter_id, reason)
        VALUES (?, ?, ?)
    ''', (group_id, user_id, reason))
    
    # Mettre à jour le compteur de signalements
    cursor.execute('''
        UPDATE groups 
        SET reported_count = reported_count + 1
        WHERE id = ?
    ''', (group_id,))
    
    # Désactiver le groupe si trop de signalements
    cursor.execute('''
        UPDATE groups 
        SET is_active = 0
        WHERE id = ? AND reported_count >= 3
    ''', (group_id,))
    
    conn.commit()
    conn.close()
    
    await update.message.reply_text("Merci pour votre signalement ! Nous allons vérifier.")
    return ConversationHandler.END

# Commandes admin (optionnel)
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != os.getenv("ADMIN_ID"):
        await update.message.reply_text("Accès refusé")
        return
    
    conn = sqlite3.connect(DB_NAME)
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

def main():
    init_db()
    
    app = Application.builder().token(TOKEN).build()
    
    # Handlers principaux
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", admin_stats))
    
    # Handler de recherche
    app.add_handler(CallbackQueryHandler(show_groups, pattern="search_all"))
    app.add_handler(CallbackQueryHandler(lambda u, c: show_groups(u, c, 'FR'), pattern="search_fr"))
    app.add_handler(CallbackQueryHandler(lambda u, c: show_groups(u, c, 'EN'), pattern="search_en"))
    
    # Handler d'ajout de groupe
    add_group_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_add_group, pattern="add_group")],
        states={
            GROUP_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_group_name)],
            GROUP_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_group_link)],
            GROUP_LANG: [CallbackQueryHandler(save_group, pattern="^lang_")]
        },
        fallbacks=[CommandHandler("cancel", lambda u,c: ConversationHandler.END)]
    )
    app.add_handler(add_group_conv)
    
    # Handler de signalement
    report_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_report, pattern="report")],
        states={
            REPORT_GROUP: [
                CallbackQueryHandler(process_report, pattern="^report_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_report)
            ]
        },
        fallbacks=[CommandHandler("cancel", lambda u,c: ConversationHandler.END)]
    )
    app.add_handler(report_conv)
    
    # Démarrage du bot
    print("Bot démarré...")
    app.run_polling()

if __name__ == "__main__":
    main()