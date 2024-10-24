from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from bot.therapy_bot import TherapyBot
from bot.conversation_states import States
from config.settings import BOT_TOKEN
import datetime

def main():
    bot = TherapyBot()
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', bot.start)],
        states={
            States.LANGUAGE_SELECTION: [
                CallbackQueryHandler(bot.handle_language_selection, pattern=r'^lang_\w+$')
            ],
            States.INITIAL_CHECKIN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_initial_checkin)
            ],
            States.FEELING_SCALE: [
                CallbackQueryHandler(bot.handle_mood_button, pattern=r'^mood_\d+$')
            ],
            States.DAILY_REFLECTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_daily_reflection)
            ],
            States.ONGOING_CONVERSATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_ongoing_conversation)
            ],
        },
        fallbacks=[CommandHandler('done', bot.handle_done)],
    )
    
    application.add_handler(conv_handler)
    
    # Add job queue for follow-ups
    job_queue = application.job_queue
    job_queue.run_repeating(bot.send_scheduled_followup, 
                           interval=datetime.timedelta(hours=5), 
                           first=datetime.timedelta(seconds=10))
    
    application.run_polling()

if __name__ == '__main__':
    main()