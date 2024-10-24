import os
from dotenv import load_dotenv

load_dotenv(override=True)

BOT_TOKEN = os.getenv('BOT_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

SUPPORTED_LANGUAGES = {
    'english': '🇬🇧 English',
    'spanish': '🇪🇸 Español',
    'french': '🇫🇷 Français',
    'german': '🇩🇪 Deutsch',
    'italian': '🇮🇹 Italiano'
}