import os
import logging
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from flask import Flask, request, jsonify

# Initialize Flask
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get environment variables
TOKEN = os.getenv("TOKEN", "7989100213:AAFLgFNp3iXdQfjL0OY-DoW43sWX8xUzms0")
WEBHOOK_URL = os.getenv("https://api.telegram.org/bot7989100213:AAFLgFNp3iXdQfjL0OY-DoW43sWX8xUzms0/setWebhook?url=https://your-render-url.onrender.com/webhook", "")
PORT = int(os.getenv("PORT", 5000))

# Track active chats
ACTIVE_CHATS = set()

# ===== Telegram Bot Functions =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message and store chat ID"""
    chat_id = update.effective_chat.id
    ACTIVE_CHATS.add(chat_id)
    
    user = update.effective_user
    welcome_text = (
        f"👋 Hello {user.first_name}! I'm SinnerB2 Bot.\n\n"
        "I can chat in groups, channels, and private chats!\n"
        "Try sending any message and I'll respond.\n\n"
        "Commands:\n"
        "/start - Show this message\n"
        "/help - Get help information\n"
        "/chatid - Get current chat ID"
    )
    
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    help_text = (
        "🤖 SinnerB2 Bot Help\n\n"
        "I'm a multi-purpose Telegram bot!\n\n"
        "Features:\n"
        "- Respond in groups, channels, and private chats\n"
        "- Remember conversation context\n"
        "- Admin tools for group management\n\n"
        "Commands:\n"
        "/start - Welcome message\n"
        "/help - This help message\n"
        "/chatid - Show current chat ID\n"
        "/groupinfo - Group information (in groups only)"
    )
    await update.message.reply_text(help_text)

async def chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send current chat ID"""
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"📬 Chat ID: `{chat_id}`", parse_mode="Markdown")

async def group_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send group information"""
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    chat = update.effective_chat
    text = (
        f"👥 Group: {chat.title}\n"
        f"🆔 ID: `{chat.id}`\n"
        f"👤 Members: {chat.get_member_count()}\n"
        f"📝 Description: {chat.description or 'None'}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages"""
    chat_id = update.effective_chat.id
    ACTIVE_CHATS.add(chat_id)
    
    user = update.effective_user
    message = update.effective_message
    
    # Customize responses based on chat type
    if update.effective_chat.type == "private":
        response = f"👋 Hello {user.first_name}! You said: {message.text}"
    else:
        response = (
            f"💬 Hey {user.mention_markdown()}! "
            f"I heard: \"{message.text}\"\n\n"
            f"Chat ID: `{chat_id}`"
        )
    
    await message.reply_text(response, parse_mode="Markdown")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ An error occurred. Please try again later."
        )

# ===== Setup and Webhook Handling =====
def setup_application():
    """Create and configure Telegram application"""
    application = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("chatid", chat_id))
    application.add_handler(CommandHandler("groupinfo", group_info))
    
    # Add message handler (all text messages except commands)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Set bot commands
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Get help"),
        BotCommand("chatid", "Get current chat ID"),
        BotCommand("groupinfo", "Get group information"),
    ]
    application.bot.set_my_commands(commands)
    
    return application

# Create Telegram application
telegram_app = setup_application()

# Flask routes
@app.route("/")
def home():
    return "🤖 SinnerB2 Bot is running! Chat with me: @sinnerb2_bot"

@app.route("/webhook", methods=["POST"])
async def webhook():
    """Handle Telegram updates via webhook"""
    update = Update.de_json(request.get_json(), telegram_app.bot)
    await telegram_app.process_update(update)
    return jsonify({"status": "ok"})

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    """Manually set webhook URL (for debugging)"""
    if not WEBHOOK_URL:
        return "WEBHOOK_URL not set in environment", 400
    
    result = telegram_app.bot.set_webhook(WEBHOOK_URL)
    return f"Webhook set: {result}", 200

# Start the application
if __name__ == "__main__":
    # Set webhook if running in production
    if WEBHOOK_URL:
        telegram_app.bot.set_webhook(WEBHOOK_URL)
        logger.info(f"Webhook set to: {WEBHOOK_URL}")
    
    # Start Flask server
    app.run(host="0.0.0.0", port=PORT)
