from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler
)
from bot.commands import start, search, admin, groups, reports
from config import Config


def setup_handlers(application: Application):
    # Handlers principaux
    application.add_handler(CommandHandler("start", start.start))
    application.add_handler(CommandHandler("stats", admin.admin_stats))

    # Handler pour le bouton Recherche (nouveau)
    application.add_handler(CallbackQueryHandler(
        search.search_groups, pattern="^search$"))  # Notez le pattern "^search$"

    # Handlers pour les sous-options de recherche
    application.add_handler(CallbackQueryHandler(
        search.show_groups, pattern="^search_all$"))
    application.add_handler(CallbackQueryHandler(
        lambda u, c: search.show_groups(u, c, 'FR'), pattern="^search_fr$"))
    application.add_handler(CallbackQueryHandler(
        lambda u, c: search.show_groups(u, c, 'EN'), pattern="^search_en$"))

    # Handler d'ajout de groupe
    add_group_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(
            groups.start_add_group, pattern="add_group")],
        states={
            Config.GROUP_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, groups.process_group_name)],
            Config.GROUP_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, groups.process_group_link)],
            Config.GROUP_LANG: [CallbackQueryHandler(
                groups.save_group, pattern="^lang_")]
        },
        fallbacks=[CommandHandler(
            "cancel", lambda u, c: ConversationHandler.END)],
        per_message=False,
        per_user=True
    )
    application.add_handler(add_group_conv)

    # Handler de signalement
    report_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(
            reports.start_report, pattern="report")],
        states={
            Config.REPORT_GROUP: [
                CallbackQueryHandler(
                    reports.process_report, pattern="^report_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               reports.save_report)
            ]
        },
        fallbacks=[CommandHandler(
            "cancel", lambda u, c: ConversationHandler.END)],
        per_message=False,
        per_user=True
    )
    application.add_handler(report_conv)
