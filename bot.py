from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os

load_dotenv()  # Charge les variables depuis .env
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Récupère le token

app = Application.builder().token(TOKEN).build()

# Commandes
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salut ! Je suis un bot 🤖")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text(f"Vous avez dit : {user_text}")

# Gestion des erreurs
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Erreur : {context.error}")

def main():
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_error_handler(error)

    # Lancement du bot
    print("Bot en écoute...")
    app.run_polling(poll_interval=3)

if __name__ == "__main__":
    main()