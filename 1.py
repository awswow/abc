import logging
import os
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from db import save_user_data  # Import the function from db.py

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define conversation states
GENDER, PHOTO, LOCATION, BIO = range(4)

# Function to ensure the images directory exists
def ensure_images_directory():
    folder_path = "images"  # Use a relative path for images folder
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

# Start the conversation
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [["Boy", "Girl", "Other"]]

    await update.message.reply_text(
        "Hi! My name is Professor Bot. I will hold a conversation with you. "
        "Send /cancel to stop talking to me.\n\n"
        "Are you a boy or a girl?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Boy or Girl?"
        ),
    )

    return GENDER

# Handle gender input
async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    context.user_data['gender'] = update.message.text  # Save gender

    await update.message.reply_text(
        "I see! Please send me a photo of yourself, "
        "so I know what you look like, or send /skip if you don't want to.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    logger.info("Photo of %s: %s", user.first_name, update.message.photo)

    # Get the file object from the photo (getting the largest photo)
    photo_file = await update.message.photo[-1].get_file()

    # Ensure the directory exists
    ensure_images_directory()

    # Set the file name (use a unique filename for each user to avoid overwriting)
    photo_filename = f"img_{user.id}.jpg"  # Use the image file name only

    # Download the photo to the specified path
    photo_path = os.path.join("images", photo_filename)  # Full path for saving the image
    await photo_file.download_to_drive(photo_path)  # Use the correct method

    logger.info("Photo of %s saved to %s", user.first_name, photo_path)

    # Store only the file name in user data
    context.user_data['photo_filename'] = photo_filename  # Save the file name only

    # Ask for the location
    await update.message.reply_text(
        "Gorgeous! Now, send me your location please, or send /skip if you don't want to."
    )

    return LOCATION

# Handle location input (city only)
async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the location and asks for some bio information."""
    user = update.message.from_user
    city = update.message.text
    logger.info("City of %s: %s", user.first_name, city)

    context.user_data['city'] = city  # Save city

    await update.message.reply_text(
        "At last, tell me something about yourself."
    )

    return BIO

# Handle skipping location
async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the location and asks for bio."""
    user = update.message.from_user
    logger.info("User %s skipped sending a location.", user.first_name)
    await update.message.reply_text(
        "You seem a bit paranoid! At last, tell me something about yourself."
    )

    return BIO

# Handle bio input
async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the bio and saves all user data to the database."""
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)

    user_data = {
        "gender": context.user_data.get('gender', ''),
        "name": user.first_name,
        "photo_filename": context.user_data.get('photo_filename', ''),  # Store file name only
        "city": context.user_data.get('city', ''),
        "bio": update.message.text,
    }

    # Save user data to the database
    save_user_data(user_data)

    await update.message.reply_text("Thank you! I hope we can talk again some day.")

    return ConversationHandler.END

# Handle cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    application = Application.builder().token("7208414520:AAF2I3T7JaDk2GJKalgnBG7OhZk6as7kccA").build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION, and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENDER: [MessageHandler(filters.Regex("^(Boy|Girl|Other)$"), gender)],
            PHOTO: [MessageHandler(filters.PHOTO, photo), CommandHandler("skip", skip_location)],
            LOCATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, location),
                CommandHandler("skip", skip_location),
            ],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
