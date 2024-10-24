from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config.settings import SUPPORTED_LANGUAGES

def create_language_keyboard() -> InlineKeyboardMarkup:
    """Create an inline keyboard for language selection."""
    keyboard = [
        [InlineKeyboardButton(display_name, callback_data=f"lang_{lang_code}")]
        for lang_code, display_name in SUPPORTED_LANGUAGES.items()
    ]
    return InlineKeyboardMarkup(keyboard)

def create_mood_scale_keyboard() -> InlineKeyboardMarkup:
    """Create an inline keyboard with mood ratings and emojis."""
    keyboard = [
        [
            InlineKeyboardButton("😢 1", callback_data="mood_1"),
            InlineKeyboardButton("😕 2", callback_data="mood_2"),
            InlineKeyboardButton("🙁 3", callback_data="mood_3"),
            InlineKeyboardButton("😐 4", callback_data="mood_4"),
            InlineKeyboardButton("😊 5", callback_data="mood_5"),
        ],
        [
            InlineKeyboardButton("🙂 6", callback_data="mood_6"),
            InlineKeyboardButton("😃 7", callback_data="mood_7"),
            InlineKeyboardButton("😄 8", callback_data="mood_8"),
            InlineKeyboardButton("😁 9", callback_data="mood_9"),
            InlineKeyboardButton("🤩 10", callback_data="mood_10"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)