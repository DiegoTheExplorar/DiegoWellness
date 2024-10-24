from datetime import datetime
import random
from typing import Dict

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.conversation_states import States
from bot.keyboards import create_language_keyboard, create_mood_scale_keyboard
from data.recommendations import SONG_RECOMMENDATIONS
from utils.llm_helper import LLMHelper

class TherapyBot:
    def __init__(self):
        self.llm_helper = LLMHelper()
        self.user_data = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the conversation and ask for language preference."""
        user_id = update.message.from_user.id
        self.user_data[user_id] = {}
        await update.message.reply_text(
            "Welcome! Please select your preferred language:\n"
            "¡Bienvenido! Por favor, seleccione su idioma preferido:\n"
            "Bienvenue! Veuillez sélectionner votre langue préférée:\n"
            "Willkommen! Bitte wählen Sie Ihre bevorzugte Sprache:\n"
            "Benvenuto! Seleziona la tua lingua preferita:",
            reply_markup=create_language_keyboard()
        )
        return States.LANGUAGE_SELECTION

    async def handle_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the language selection callback."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        selected_language = query.data.split('_')[1]
        self.user_data[user_id] = {'language': selected_language}
        
        welcome_messages = {
            'english': "How are you feeling today? Would you like to tell me about your day?",
            'spanish': "¿Cómo te sientes hoy? ¿Te gustaría contarme sobre tu día?",
            'french': "Comment vous sentez-vous aujourd'hui? Voulez-vous me parler de votre journée?",
            'german': "Wie fühlen Sie sich heute? Möchten Sie mir von Ihrem Tag erzählen?",
            'italian': "Come ti senti oggi? Vorresti raccontarmi della tua giornata?"
        }
        
        await query.edit_message_text(welcome_messages[selected_language])
        return States.INITIAL_CHECKIN

    async def handle_initial_checkin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the user's initial response about their day."""
        user_id = update.message.from_user.id
        message_text = update.message.text
        
        if user_id in self.user_data:
            self.user_data[user_id].update({
                'last_message': message_text,
                'timestamp': datetime.now().isoformat()
            })
        else:
            self.user_data[user_id] = {
                'last_message': message_text,
                'timestamp': datetime.now().isoformat(),
                'language': 'english'
            }
        
        language = self.user_data[user_id]['language']
        mood_scale_messages = {
            'english': "Thank you for sharing. How would you rate your mood today?",
            'spanish': "Gracias por compartir. ¿Cómo calificarías tu estado de ánimo hoy?",
            'french': "Merci d'avoir partagé. Comment évalueriez-vous votre humeur aujourd'hui?",
            'german': "Danke fürs Teilen. Wie würden Sie Ihre Stimmung heute bewerten?",
            'italian': "Grazie per aver condiviso. Come valuteresti il tuo umore oggi?"
        }
        
        await update.message.reply_text(
            mood_scale_messages[language],
            reply_markup=create_mood_scale_keyboard()
        )
        return States.FEELING_SCALE

    async def handle_mood_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the mood rating button press."""
        query = update.callback_query
        await query.answer()
        
        mood_rating = int(query.data.split('_')[1])
        user_id = query.from_user.id
        
        self.user_data[user_id]['mood_rating'] = mood_rating
        
        if mood_rating <= 4:
            self.user_data[user_id]['mood_category'] = 'sad'
            self.user_data[user_id]['needs_followup'] = True
        elif mood_rating <= 7:
            self.user_data[user_id]['mood_category'] = 'anxious'
            self.user_data[user_id]['needs_followup'] = True
        else:
            self.user_data[user_id]['mood_category'] = 'happy'
            self.user_data[user_id]['needs_followup'] = False
        
        response = await self.llm_helper.get_response(
            f"User rated their mood as {mood_rating}/10. Generate a supportive response and ask an appropriate follow-up question.",
            self.user_data[user_id]
        )
        
        mood_display_messages = {
            'english': "Your mood:",
            'spanish': "Tu estado de ánimo:",
            'french': "Votre humeur:",
            'german': "Ihre Stimmung:",
            'italian': "Il tuo umore:"
        }
        
        language = self.user_data[user_id]['language']
        await query.edit_message_text(
            f"{mood_display_messages[language]} {mood_rating}/10\n\n{response}"
        )
        
        return States.DAILY_REFLECTION

    async def handle_daily_reflection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the user's reflection and provide support."""
        user_id = update.message.from_user.id
        message_text = update.message.text
        
        user_data = self.user_data.get(user_id, {})
        mood_category = user_data.get('mood_category', 'happy')
        
        user_data['last_message'] = message_text
        
        song, artist, link = random.choice(SONG_RECOMMENDATIONS[mood_category])
        user_data['song'] = (song, artist, link)
        
        response = await self.llm_helper.get_response(
            f"User shared their reflection: '{message_text}'. Their mood category is {mood_category}. "
            f"Generate a supportive response without ending the conversation.",
            user_data
        )
        
        await update.message.reply_text(response)
        return States.ONGOING_CONVERSATION

    async def handle_ongoing_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle ongoing conversation with the user."""
        user_id = update.message.from_user.id
        message_text = update.message.text
        
        if user_id in self.user_data:
            self.user_data[user_id]['last_message'] = message_text
        
        response = await self.llm_helper.get_response(
            f"User continues the conversation with: '{message_text}'. Respond empathetically and encourage further discussion.",
            self.user_data.get(user_id, {})
        )
        
        await update.message.reply_text(response)
        return States.ONGOING_CONVERSATION

    async def handle_done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the end of conversation and provide song recommendation."""
        user_id = update.message.from_user.id
        user_data = self.user_data.get(user_id, {})
        language = user_data.get('language', 'english')
        
        song_info = user_data.get('song')
        
        if song_info:
            song, artist, link = song_info
            goodbye_messages = {
                'english': f"Thank you for sharing with me today. Here's a song that might match your mood: {song} by {artist}\nYou can listen to it at: {link}",
                'spanish': f"Gracias por compartir conmigo hoy. Aquí hay una canción que podría coincidir con tu estado de ánimo: {song} de {artist}\nPuedes escucharla en: {link}",
                'french': f"Merci d'avoir partagé avec moi aujourd'hui. Voici une chanson qui pourrait correspondre à votre humeur: {song} par {artist}\nVous pouvez l'écouter sur: {link}",
                'german': f"Danke, dass Sie heute mit mir geteilt haben. Hier ist ein Lied, das zu Ihrer Stimmung passen könnte: {song} von {artist}\nSie können es hier hören: {link}",
                'italian': f"Grazie per aver condiviso con me oggi. Ecco una canzone che potrebbe adattarsi al tuo umore: {song} di {artist}\nPuoi ascoltarla su: {link}"
            }
        else:
            goodbye_messages = {
                'english': "Thank you for chatting. Feel free to come back anytime!",
                'spanish': "Gracias por charlar. ¡Vuelve cuando quieras!",
                'french': "Merci d'avoir discuté. N'hésitez pas à revenir!",
                'german': "Danke für das Gespräch. Kommen Sie gerne jederzeit wieder!",
                'italian': "Grazie per la chiacchierata. Torna quando vuoi!"
            }
        
        await update.message.reply_text(goodbye_messages[language])
        return ConversationHandler.END

    async def send_scheduled_followup(self, context: ContextTypes.DEFAULT_TYPE):
        """Send scheduled follow-up messages to users who were feeling down."""
        current_time = datetime.now()
        
        for user_id, data in self.user_data.items():
            if data.get('needs_followup'):
                last_message_time = datetime.fromisoformat(data['timestamp'])
                if (current_time - last_message_time).days >= 1:
                    try:
                        follow_up_message = await self.llm_helper.get_response(
                            "Generate a caring follow-up message for a user who was feeling down yesterday.",
                            data
                        )
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=follow_up_message
                        )
                        data['needs_followup'] = False
                    except Exception as e:
                        print(f"Failed to send follow-up to user {user_id}: {e}")