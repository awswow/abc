import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from db import save_user_data, find_user  # Assuming db.py handles database operations

# Define states for the conversation
GENDER, PHOTO, LOCATION, BIO = range(4)

# Start the conversation or ask to update profile or search
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the profile creation process or ask user to update profile or search for users if already in DB."""
    user = update.message.from_user
    chat_id = user.id

    # Check if the user already exists in the database
    existing_user = find_user(chat_id)
    
    if existing_user:
        # If user exists, offer options to either update their profile or search for users
        keyboard = [
            [InlineKeyboardButton("Update Profile", callback_data="update_profile")],
            [InlineKeyboardButton("Search Users", callback_data="search_users")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Welcome back! You already have a profile. What would you like to do?",
            reply_markup=reply_markup
        )
        return -1  # End conversation if user is found in DB
    
    else:
        # If user does not exist, start profile creation process
        keyboard = [
            ["Boy", "Girl", "Other"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, input_field_placeholder="Boy or Girl?")
        
        await update.message.reply_text(
            "Hi! My name is Professor Bot. I will hold a conversation with you. Send /cancel to stop talking to me.\n\n"
            "Are you a boy, girl, or other?",
            reply_markup=reply_markup
        )
        
        return GENDER  # Proceed to GENDER state

# Handle gender input and move to photo state
async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    gender = update.message.text  # Get gender input from user
    context.user_data['gender'] = gender  # Save gender to user data

    # Reply to the user and ask for a photo
    await update.message.reply_text(
        f"Got it! You're a {gender}. Please send me a photo of yourself, "
        "or send /skip if you don't want to upload one."
    )
    
    return PHOTO

# Handle photo input and move to location state
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo = update.message.photo[-1].file_id  # Save the photo file ID
    context.user_data['photo'] = photo  # Save photo

    # Ask for location (city)
    await update.message.reply_text(
        "Nice photo! Now, please tell me your city, or send /skip if you don't want to share."
    )

    return LOCATION

# Handle location input and move to bio state
async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the location (city) and asks for bio."""
    city = update.message.text
    context.user_data['city'] = city  # Save city to user data

    # Ask for bio
    await update.message.reply_text("Great! Now, tell me something about yourself (your bio).")

    return BIO

# Handle bio input and save user data
async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the bio and saves all user data to the database."""
    bio = update.message.text
    context.user_data['bio'] = bio  # Save bio to user data

    # Prepare user data
    user_data = {
        "chat_id": update.message.from_user.id,
        "gender": context.user_data['gender'],
        "name": update.message.from_user.first_name,
        "photo_filename": context.user_data.get('photo', ''),  # Save photo ID or filename
        "city": context.user_data['city'],
        "bio": bio,
        "age": 0,  # Default age, you can add an age step if needed
        "username": update.message.from_user.username
    }

    # Save to the database
    save_user_data(user_data)

    await update.message.reply_text("Thanks for creating your profile!")

    return -1  # End the conversation

# Handle skipping photo
async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the location and bio input."""
    await update.message.reply_text("Okay, no location shared. Tell me something about yourself.")

    return BIO

# Handle the update profile callback query
async def update_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the 'Update Profile' button press."""
    user = update.message.from_user
    chat_id = user.id

    # Fetch user profile from database using chat_id
    existing_user = find_user(chat_id)
    if existing_user:
        # If user exists, ask if they want to update their profile
        keyboard = [
            ["Change Name", "Change Gender", "Change Photo", "Change City", "Change Bio"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

        await update.message.reply_text(
            "What would you like to update? Choose an option below.",
            reply_markup=reply_markup
        )

        return -1  # End the conversation, the next action will be handled in the respective state
    else:
        # If user does not exist, initiate the profile creation process
        keyboard = [
            ["Boy", "Girl", "Other"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, input_field_placeholder="Boy or Girl?")
        
        await update.message.reply_text(
            "Hi! My name is Professor Bot. I will help you set up your profile. Please select your gender.",
            reply_markup=reply_markup
        )
        
        return GENDER  # Proceed to GENDER state
# Handle the update photo callback query
async def update_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the update photo process."""
    query = update.callback_query
    query.answer()  # Acknowledge the callback query
    
    await query.edit_message_text("Please send a new photo to update your profile.")

    return PHOTO

# Handle the update location callback query
async def update_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the update location process."""
    query = update.callback_query
    query.answer()  # Acknowledge the callback query
    
    await query.edit_message_text("Please send your new city to update your location.")

    return LOCATION

# Handle the update bio callback query
async def update_bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the update bio process."""
    query = update.callback_query
    query.answer()  # Acknowledge the callback query
    
    await query.edit_message_text("Please send your new bio to update your profile.")

    return BIO

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle cancellation of the conversation."""
    await update.message.reply_text(
        "Goodbye! Your profile creation has been cancelled. If you'd like to start again, just send /start."
    )
    return -1  # End the conversation
