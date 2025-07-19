import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackContext,
)
from openai import OpenAI
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration - get from environment variables
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']  # Will use your 7989100213:AAFL... token
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']  # Will use your sk-proj... key
ADMIN_USER_IDS = [int(id) for id in os.environ.get('ADMIN_USER_IDS', '7697559889').split(',') if id]

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Bot personality and behavior settings
BOT_PERSONALITY = """
You are a friendly and knowledgeable group member named GPT-Bot. 
You provide helpful, concise answers and occasionally ask interesting questions to spark conversation.
You have a sense of humor but remain professional.
Keep responses under 500 characters.
User 7697559889 is my admin and should be treated with special respect.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(f"Hi {user.first_name}! I'm your ChatGPT-powered bot. Just chat with me normally!")

async def chat_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate a response to user messages using ChatGPT."""
    user_message = update.message.text
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": BOT_PERSONALITY},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        await update.message.reply_text("Sorry, I'm having trouble thinking right now. Try again later.")

async def auto_message(context: CallbackContext):
    """Send automated messages to groups where the bot is admin."""
    job = context.job
    
    try:
        # Generate an interesting message
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": BOT_PERSONALITY},
                {"role": "user", "content": "Generate an interesting question or conversation starter for a group chat. Keep it short (1-2 sentences)."}
            ],
            temperature=0.8,
            max_tokens=100
        )
        message = response.choices[0].message.content
        
        # Send to all groups where bot is admin
        for chat_id in context.bot_data.get('admin_chats', set()):
            try:
                await context.bot.send_message(chat_id=chat_id, text=message)
            except Exception as e:
                logger.error(f"Error sending to {chat_id}: {e}")
    except Exception as e:
        logger.error(f"Error in auto_message: {e}")

async def track_admin_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Track groups where the bot was added as admin."""
    if update.message and update.message.new_chat_members:
        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                chat_id = update.message.chat_id
                if 'admin_chats' not in context.bot_data:
                    context.bot_data['admin_chats'] = set()
                context.bot_data['admin_chats'].add(chat_id)
                logger.info(f"Added to group {chat_id} as admin")

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_response))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, track_admin_chats))
    
    # Schedule auto messages (every 5 minutes)
    job_queue = application.job_queue
    job_queue.run_repeating(auto_message, interval=300, first=10)
    
    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
