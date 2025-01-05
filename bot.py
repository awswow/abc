from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, filters, ConversationHandler
from db import save_user_data, find_user, update_user_profile
import logging

GENDER, PHOTO, CITY, BIO, AGE, UPDATE_PROFILE = range(6)

async def start(update: Update, context: CallbackContext):
    """Handle start command and initiate conversation."""
    user = update.message.from_user
    await update.message.reply_text("Welcome! What's your gender? (Male/Female/Other)")
    return GENDER

async def gender(update: Update, context: CallbackContext):
    """Handle gender input."""
    user = update.message.from_user
    context.user_data['gender'] = update.message.text
    await update.message.reply_text("Please send a photo.")
    return PHOTO

async def photo(update: Update, context: CallbackContext):
    """Handle photo input."""
    user = update.message.from_user
    context.user_data['photo'] = update.message.photo[-1].file_id
    await update.message.reply_text("What's your city?")
    return CITY

async def city(update: Update, context: CallbackContext):
    """Handle city input."""
    user = update.message.from_user
    context.user_data['city'] = update.message.text
    await update.message.reply_text("Tell me about yourself (bio).")
    return BIO

async def bio(update: Update, context: CallbackContext):
    """Handle bio input."""
    user = update.message.from_user
    context.user_data['bio'] = update.message.text
    await update.message.reply_text("How old are you?")
    return AGE

async def age(update: Update, context: CallbackContext):
    """Handle age input."""
    user = update.message.from_user
    context.user_data['age'] = update.message.text

    # Save user data to DB
    user_data = {
        'chat_id': user.id,
        'gender': context.user_data['gender'],
        'name': user.first_name,
        'photo_filename': context.user_data['photo'],
        'city': context.user_data['city'],
        'bio': context.user_data['bio'],
        'age': context.user_data['age'],
        'username': user.username
    }
    save_user_data(user_data)

    await update.message.reply_text("Your profile has been saved successfully!")
    return ConversationHandler.END

async def update_profile(update: Update, context: CallbackContext):
    """Handle update profile option."""
    user = update.message.from_user
    user_data = find_user(user.id)
    if user_data:
        await update.message.reply_text(f"Current profile:\nName: {user_data['name']}\nCity: {user_data['city']}\nAge: {user_data['age']}")
        await update.message.reply_text("What would you like to update? (Gender/Name/Bio/City/Age)")
        return UPDATE_PROFILE
    else:
        await update.message.reply_text("You haven't created a profile yet.")
        return ConversationHandler.END

async def update_gender(update: Update, context: CallbackContext):
    """Handle updating gender."""
    user = update.message.from_user
    new_gender = update.message.text
    update_user_profile(user.id, {'gender': new_gender})
    await update.message.reply_text(f"Your gender has been updated to {new_gender}.")
    return ConversationHandler.END

async def update_name(update: Update, context: CallbackContext):
    """Handle updating name."""
    user = update.message.from_user
    new_name = update.message.text
    update_user_profile(user.id, {'name': new_name})
    await update.message.reply_text(f"Your name has been updated to {new_name}.")
    return ConversationHandler.END

async def update_bio(update: Update, context: CallbackContext):
    """Handle updating bio."""
    user = update.message.from_user
    new_bio = update.message.text
    update_user_profile(user.id, {'bio': new_bio})
    await update.message.reply_text(f"Your bio has been updated to {new_bio}.")
    return ConversationHandler.END

async def update_city(update: Update, context: CallbackContext):
    """Handle updating city."""
    user = update.message.from_user
    new_city = update.message.text
    update_user_profile(user.id, {'city': new_city})
    await update.message.reply_text(f"Your city has been updated to {new_city}.")
    return ConversationHandler.END

async def update_age(update: Update, context: CallbackContext):
    """Handle updating age."""
    user = update.message.from_user
    new_age = update.message.text
    update_user_profile(user.id, {'age': new_age})
    await update.message.reply_text(f"Your age has been updated to {new_age}.")
    return ConversationHandler.END

async def update_photo(update: Update, context: CallbackContext):
    """Handles the update photo option."""
    user = update.message.from_user
    new_photo = update.message.photo[-1].file_id
    update_user_profile(user.id, {'photo_filename': new_photo})
    await update.message.reply_text(f"Your photo has been updated.")
    return ConversationHandler.END

async def skip_city(update: Update, context: CallbackContext):
    """Handle skipping city input."""
    await update.message.reply_text("City skipped.")
    return BIO

async def cancel(update: Update, context: CallbackContext):
    """Cancel the current conversation and reset the state."""
    await update.message.reply_text("Conversation canceled. You can start again anytime by typing /start.")
    return ConversationHandler.END
