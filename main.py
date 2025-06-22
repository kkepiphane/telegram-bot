import asyncio
from config import Config
from bot.database import init_db
from bot.handlers import setup_handlers
from telegram.ext import Application


async def main():
    try:
        init_db()

        application = Application.builder().token(Config.TOKEN).build()
        setup_handlers(application)

        print("Bot démarré...")
        await application.initialize()
        await application.start()
        await application.updater.start_polling()

        while True:
            await asyncio.sleep(3600)
    except Exception as e:
        print(f"Erreur critique: {e}")
    finally:
        print("Bot arrêté")

if __name__ == "__main__":
    asyncio.run(main())
