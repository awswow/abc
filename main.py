from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from bot import start, gender, photo, location, skip_location, bio, cancel, update_profile  # Import necessary functions from bot.py
from config import BOT_TOKEN  # Import the bot token from config.py

# Define the conversation states
GENDER, PHOTO, LOCATION, BIO = range(4)

async def main() -> None:
    """Run the bot."""
    # Create an Application instance with your bot token
    application = Application.builder().token(BOT_TOKEN).build()

    # Create a conversation handler with entry points, states, and fallbacks
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],  # The entry point for the conversation
        states={
            GENDER: [MessageHandler(filters.Regex("^(Boy|Girl|Other)$"), gender)],  # Handles gender input
            PHOTO: [MessageHandler(filters.PHOTO, photo), CommandHandler("skip", skip_location)],  # Handles photo input
            LOCATION: [  # Handles location input
                MessageHandler(filters.TEXT & ~filters.COMMAND, location),
                CommandHandler("skip", skip_location),
            ],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],  # Handles bio input
        },
        fallbacks=[CommandHandler("cancel", cancel)],  # Handle cancellation command
    )

    # Add the conversation handler to the application
    application.add_handler(conv_handler)

    # Add command handler to update profile
    application.add_handler(CommandHandler("update_profile", update_profile))

    # Run the bot with polling
    await application.run_polling()

# If this is the main script, run the bot
if __name__ == "__main__":
    # Directly call the async main function
    import asyncio
    asyncio.get_event_loop().run_until_complete(main())
