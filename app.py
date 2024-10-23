import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
import datetime
import json
import random
import os
from groq import Groq
from typing import Dict, List, Tuple
"""
from dotenv import load_dotenv
load_dotenv(override=True)
"""
# States for conversation
INITIAL_CHECKIN, FEELING_SCALE, DAILY_REFLECTION, SONG_RECOMMENDATION, ONGOING_CONVERSATION = range(5)

# Dictionary to store user data
user_data = {}

class TherapyBot:
    def __init__(self):
        groq_api_key = os.getenv('GROQ_API_KEY')
        self.groq_client = Groq(api_key=groq_api_key)
        # Song recommendations based on moods
        # Song recommendations with URLs
        self.song_recommendations = {
            'sad': [
                ('The Sun Will Come Up, the Seasons Will Change', 'Nina Nesbitt', 'https://open.spotify.com/track/46fCdWJ7Ddo2QffVE4zbRu?si=bdad68fa24d0423a'),
                ('Better Place', 'Rachel Platten', 'https://open.spotify.com/track/7xbXQeepclfQNqI3mLPb3c?si=1125dd3893a546e2'),
                ('Rainbow', 'Kacey Musgraves', 'https://open.spotify.com/track/79qxwHypONUt3AFq0WPpT9?si=33868d43ca624b85')
            ],
            'anxious': [
                ('Breathin', 'Ariana Grande', 'https://open.spotify.com/track/4OafepJy2teCjYJbvFE60J?si=67340b220c0f4f35'),
                ('The Middle', 'Jimmy Eat World', 'https://open.spotify.com/track/09IStsImFySgyp0pIQdqAc?si=bfb8da788ed340ca'),
                ('Shake It Out', 'Florence + The Machine', 'https://open.spotify.com/track/71iSmEeF0qRVyULABxP75P?si=12a5b15b7d9d4505')
            ],
            'happy': [
                ('Good as Hell', 'Lizzo', 'https://open.spotify.com/track/6KgBpzTuTRPebChN0VTyzV?si=830eeb16a65644d8'),
                ('Walking on Sunshine', 'Katrina & The Waves', 'https://open.spotify.com/track/05wIrZSwuaVWhcv5FfqeH0?si=652baf0e3acb48bc'),
                ('Happy', 'Pharrell Williams', 'https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH?si=60b7e9090e9d4e84')
            ]
        }


    def create_mood_scale_keyboard(self) -> InlineKeyboardMarkup:
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
                InlineKeyboardButton("🌟 10", callback_data="mood_10"),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    async def get_llm_response(self, prompt: str, user_context: Dict = None) -> str:
        """Get a response from the Groq LLM API."""
        system_prompt = """You are a compassionate and supportive therapy chat bot. Your responses should be:
        1. Empathetic and understanding
        2. Encouraging but not dismissive of negative feelings
        3. Professional while maintaining a warm tone
        4. Keep to at most 3-4 sentences per response
        Never recommend medical advice or try to diagnose conditions. But give tips on how to overcome negative feelings."""
        
        context = ""
        if user_context:
            context = f"\nUser's previous mood rating: {user_context.get('mood_rating', 'Unknown')}\nLast message: {user_context.get('last_message', 'None')}"
        
        try:
            completion = self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{context}\n\nUser message: {prompt}"}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error getting LLM response: {e}")
            return self._get_fallback_response(prompt)

    def _get_fallback_response(self, prompt: str) -> str:
        """Provide a fallback response if LLM call fails."""
        fallback_responses = {
            "default": "I understand how you're feeling. Would you like to tell me more about that?",
            "low_mood": "I hear that you're going through a difficult time. Remember that it's okay to not be okay.",
            "positive": "I'm glad you're feeling good! What's been helping you maintain this positive mood?"
        }
        return fallback_responses["default"]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the conversation."""
        response = await self.get_llm_response(
            "Generate a warm welcome message for a new user starting therapy chat."
        )
        await update.message.reply_text(
            f"{response}\n\nHow are you feeling today? Would you like to tell me about your day?"
        )
        return INITIAL_CHECKIN

    async def handle_initial_checkin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the user's initial response about their day."""
        user_id = update.message.from_user.id
        message_text = update.message.text
        
        user_data[user_id] = {
            'last_message': message_text,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        # Send mood scale with buttons
        await update.message.reply_text(
            "Thank you for sharing. How would you rate your mood today?",
            reply_markup=self.create_mood_scale_keyboard()
        )
        return FEELING_SCALE

    async def handle_mood_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the mood rating button press."""
        query = update.callback_query
        await query.answer()  # Acknowledge the button press
        
        # Extract mood rating from callback data
        mood_rating = int(query.data.split('_')[1])
        user_id = query.from_user.id
        
        # Update user data
        user_data[user_id]['mood_rating'] = mood_rating
        
        # Categorize mood
        if mood_rating <= 4:
            user_data[user_id]['mood_category'] = 'sad'
        elif mood_rating <= 7:
            user_data[user_id]['mood_category'] = 'anxious'
        else:
            user_data[user_id]['mood_category'] = 'happy'
        
        # Get LLM response
        response = await self.get_llm_response(
            f"User rated their mood as {mood_rating}/10. Generate a supportive response and ask an appropriate follow-up question.",
            user_data[user_id]
        )
        
        # Edit the original message to remove the keyboard and send the response
        await query.edit_message_text(
            f"Your mood: {mood_rating}/10\n\n{response}"
        )
        
        return DAILY_REFLECTION

    async def handle_daily_reflection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Provide support and song recommendations based on the user's mood."""
        user_id = update.message.from_user.id
        mood_category = user_data[user_id]['mood_category']
        message_text = update.message.text
        
        # Get song recommendation (will be used at the end of the conversation)
        song, artist,link = random.choice(self.song_recommendations[mood_category])
        
        # Get LLM response
        response = await self.get_llm_response(
            f"User shared their reflection: '{message_text}'. Their mood category is {mood_category}. "
            f"Generate a supportive response without ending the conversation.",
            user_data[user_id]
        )
        
        # Store song recommendation in user_data to suggest later
        user_data[user_id]['song'] = (song, artist,link)
        
        # Continue the conversation instead of ending it
        await update.message.reply_text(response)
        
        return ONGOING_CONVERSATION  # Transition to ONGOING_CONVERSATION

    async def handle_ongoing_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Continue the conversation until the user decides to stop."""
        user_id = update.message.from_user.id
        message_text = update.message.text
        
        # Get LLM response
        response = await self.get_llm_response(
            f"User continues the conversation with: '{message_text}'. Respond empathetically and encourage further discussion.",
            user_data[user_id]
        )
        
        await update.message.reply_text(response)
        
        # The conversation keeps going until the user types /done
        return ONGOING_CONVERSATION

    async def handle_done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle when the user is done with the conversation."""
        user_id = update.message.from_user.id
        
        # Retrieve stored song recommendation
        song, artist,link = user_data[user_id].get('song', (None, None))
        
        if song and artist:
            response = await self.get_llm_response(
                f"User has indicated they are done. Recommend the song '{song}' by {artist} to close the conversation warmly.",
                user_data[user_id]
            )
            await update.message.reply_text(f"{response}\n\nHere's a song that might match your mood: {song} by {artist} you can listen to it at: {link}")
        else:
            await update.message.reply_text("Thank you for chatting. Feel free to come back anytime!")
        
        return ConversationHandler.END



    async def send_scheduled_followup(self, context: ContextTypes.DEFAULT_TYPE):
        """Send follow-up messages to users who were feeling down."""
        current_time = datetime.datetime.now()
        
        for user_id, data in user_data.items():
            if data.get('needs_followup'):
                last_message_time = datetime.datetime.fromisoformat(data['timestamp'])
                # If it's been about 24 hours since their last check-in
                if (current_time - last_message_time).days >= 1:
                    try:
                        # Get a fresh follow-up message
                        follow_up_message = await self.get_llm_response(
                            "Generate a caring follow-up message for a user who was feeling down yesterday.",
                            data
                        )
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=follow_up_message
                        )
                        # Reset the follow-up flag
                        data['needs_followup'] = False
                    except Exception as e:
                        print(f"Failed to send follow-up to user {user_id}: {e}")

# Adjust the conversation handler to include ONGOING_CONVERSATION and /done command
def main():
    token = os.getenv('BOT_TOKEN')
    
    bot = TherapyBot()
    application = Application.builder().token(token).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', bot.start)],
        states={
            INITIAL_CHECKIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_initial_checkin)],
            FEELING_SCALE: [CallbackQueryHandler(bot.handle_mood_button, pattern=r'^mood_\d+$')],
            DAILY_REFLECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_daily_reflection)],
            ONGOING_CONVERSATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_ongoing_conversation)],
        },
        fallbacks=[CommandHandler('done', bot.handle_done)],  # User can type /done to end
    )
    
    application.add_handler(conv_handler)
    
    job_queue = application.job_queue
    job_queue.run_repeating(bot.send_scheduled_followup, interval=datetime.timedelta(hours=5), first=datetime.timedelta(seconds=10))
    
    application.run_polling()

if __name__ == '__main__':
    main()