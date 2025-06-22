# Otaku Finder Bot 🤖✨

Un bot Telegram pour découvrir et partager des groupes communautaires otaku.

## Fonctionnalités 🌟

- 🔍 Rechercher des groupes par langue (FR/EN/Tous)
- 📌 Proposer de nouveaux groupes
- ⚠️ Signaler des groupes inappropriés
- 📊 Statistiques admin (groupes actifs, signalements)

## Installation 💻

### Prérequis
- Python 3.10+
- Compte Telegram avec @BotFather
- Accès à une base de données SQLite

### Configuration

1. Clonez le dépôt :
```bash
  git clone https://github.com/kkepiphane/telegram-bot.git
  cd telegram-bot bash ```

2. Configurez l'environnement:
  python -m venv venv
  source venv/bin/activate  # Linux/Mac
  venv\Scripts\activate     # Windows

3. Installez les dépendances :
   pip install -r requirements.txt

4. Créez un fichier .env :
   TELEGRAM_BOT_TOKEN=votre_token_bot
   ADMIN_ID=votre_id_telegram

   
