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

# Hardcoded configuration (replace with your actual values)
TOKEN = "7989100213:AAFLgFNp3iXdQfjL0OY-DoW43sWX8xUzms0"
WEBHOOK_URL = "https://your-render-service.onrender.com/webhook"  # ← CHANGE THIS
PORT = 10000
HOST = "0.0.0.0"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I'm your SinnerB2 Bot!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🔊 Echo: {update.message.text}")

async def configure_webhook(app: Application):
    """Set up webhook and commands"""
    await app.bot.set_webhook(
        url=WEBHOOK_URL,
        drop_pending_updates=True,
        allowed_updates=["message", "edited_message"]
    )
    await app.bot.set_my_commands([
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Get help")
    ])
    logger.info(f"Webhook configured for {WEBHOOK_URL}")

def create_app():
    """Initialize application"""
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Configure webhook on startup
    application.run_webhook(
        listen=HOST,
        port=PORT,
        webhook_url=WEBHOOK_URL,
        secret_token='WEBHOOK_SECRET',  # Optional security
        post_init=configure_webhook
    )
    return application

# Flask routes
@app.route('/')
def home():
    return "🤖 Bot is running! Webhook: " + WEBHOOK_URL

@app.route('/webhook', methods=['POST'])
async def webhook_handler():
    update = Update.de_json(await request.get_json(), telegram_app.bot)
    await telegram_app.process_update(update)
    return '', 200

# Initialize
telegram_app = create_app()

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
