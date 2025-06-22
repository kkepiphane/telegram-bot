from telegram.constants import ChatAction
from telegram.ext import ContextTypes


async def is_valid_group(link: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        # Nettoyage et extraction du username
        if link.startswith('https://t.me/'):
            username = link[13:]
        elif link.startswith('t.me/'):
            username = link[5:]
        else:
            return False
        
        # Suppression des paramètres de l'URL
        username = username.split('?')[0]
        
        # Vérification alternative sans nécessiter que le bot soit membre
        try:
            await context.bot.get_chat(f"@{username}")
            return True
        except Exception as e:
            print(f"Impossible de vérifier le chat directement: {e}")
            
            # Deuxième méthode de vérification
            try:
                await context.bot.send_chat_action(chat_id=f"@{username}", action=ChatAction.TYPING)
                return True
            except:
                return False
                
    except Exception as e:
        print(f"Erreur de validation: {e}")
        return False