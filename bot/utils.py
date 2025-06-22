from telegram.constants import ChatAction
from telegram.ext import ContextTypes


async def is_valid_group(link: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        # Nettoyer le lien
        if link.startswith('https://'):
            clean_link = link.replace('https://', '')
        else:
            clean_link = link

        if clean_link.startswith('t.me/'):
            chat_id = '@' + clean_link.split('t.me/')[1]
        else:
            return False

        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        return True
    except Exception as e:
        print(f"Validation du lien échouée: {e}")
        return False
