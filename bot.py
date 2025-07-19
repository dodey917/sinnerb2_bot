import os
import logging
import asyncio
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from flask import Flask, request, jsonify
from waitress import serve

# Configuration - MUST UPDATE THESE!
TOKEN = "7989100213:AAFLgFNp3iXdQfjL0OY-DoW43sWX8xUzms0"
WEBHOOK_URL = "https://sinnerb2-bot.onrender.com/webhook"  # Must match your Render URL
PORT = 10000  # Must match Render environment
HOST = "0.0.0.0"

# Initialize Flask
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text("👋 Hello! I'm your SinnerB2 Bot!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo messages"""
    await update.message.reply_text(f"🔊 Echo: {update.message.text}")

def create_application():
    """Create Telegram application"""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    return application

# Initialize
telegram_app = create_application()

# Flask Routes
@app.route('/')
def home():
    return "🤖 Bot is running!"

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Handle Telegram updates"""
    json_data = await request.get_json()
    update = Update.de_json(json_data, telegram_app.bot)
    await telegram_app.process_update(update)
    return jsonify({"status": "ok"})

async def setup():
    """Configure bot commands and webhook"""
    # Set bot commands
    await telegram_app.bot.set_my_commands([
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Get help")
    ])
    
    # Set webhook
    await telegram_app.bot.set_webhook(
        url=WEBHOOK_URL,
        drop_pending_updates=True,
        allowed_updates=["message", "edited_message"]
    )
    logger.info(f"✅ Webhook configured for {WEBHOOK_URL}")

def run():
    """Start the application"""
    # Run async setup
    asyncio.run(setup())
    
    # Start Waitress server
    serve(app, host=HOST, port=PORT)

if __name__ == '__main__':
    run()
