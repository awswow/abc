from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from bot import start, gender, photo, city, bio, age, update_profile, update_gender, update_name, update_bio, update_city, update_age, update_photo, cancel
from config import BOT_TOKEN
import logging

# Define the conversation handler states
GENDER, PHOTO, CITY, BIO, AGE, UPDATE_PROFILE = range(6)

# Set up logging to console
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Conversation handler
conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],  # Start command
    states={
        GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
        PHOTO: [MessageHandler(filters.PHOTO, photo)],
        CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, city)],
        BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
        UPDATE_PROFILE: [
            CallbackQueryHandler(update_gender, pattern="update_gender"),
            CallbackQueryHandler(update_name, pattern="update_name"),
            CallbackQueryHandler(update_bio, pattern="update_bio"),
            CallbackQueryHandler(update_city, pattern="update_city"),
            CallbackQueryHandler(update_age, pattern="update_age"),
            CallbackQueryHandler(update_photo, pattern="update_photo")
        ]
    },
    fallbacks=[CommandHandler('cancel', cancel)],  # Cancel command
)

def main():
    """Start the bot and add handlers."""
    # Replace 'YOUR_TOKEN' with your actual bot token
    application = Application.builder().token(BOT_TOKEN).build()

    # Add conversation handler
    application.add_handler(conversation_handler)

    # Start polling for updates
    application.run_polling()

if __name__ == '__main__':
    main()
