import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    ADMIN_ID = os.getenv("ADMIN_ID")
    DB_NAME = "otaku_groups.db"
    
    # États pour les conversations
    GROUP_NAME, GROUP_LINK, GROUP_LANG = range(3)
    REPORT_GROUP = 1